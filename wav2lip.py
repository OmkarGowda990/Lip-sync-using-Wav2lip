# -*- coding: utf-8 -*-
"""Wav2Lip.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1NyQx361E-z9Jj1ButvC6__mVCS_gwT83
"""

# Commented out IPython magic to ensure Python compatibility.

#@title <h1>Step1: Setup Wav2Lip</h1>
!rm -rf /content/sample_data
!mkdir /content/sample_data

!git clone https://github.com/justinjohn0306/Wav2Lip

#download the pretrained model
!wget 'https://iiitaphyd-my.sharepoint.com/personal/radrabha_m_research_iiit_ac_in/_layouts/15/download.aspx?share=EdjI7bZlgApMqsVoEUUXpLsBxqXbn5z8VTmoxp55YNDcIA' -O '/content/Wav2Lip/checkpoints/wav2lip_gan.pth'
a = !pip install https://raw.githubusercontent.com/AwaleSajil/ghc/master/ghc-1.0-py3-none-any.whl

# !pip uninstall tensorflow tensorflow-gpu
!cd Wav2Lip && pip install -r requirements.txt

#download pretrained model for face detection
!wget "https://www.adrianbulat.com/downloads/python-fan/s3fd-619a316812.pth" -O "/content/Wav2Lip/face_detection/detection/sfd/s3fd.pth"

!pip install ffmpeg-python


from IPython.display import HTML, Audio
from google.colab.output import eval_js
from base64 import b64decode
import numpy as np
from scipy.io.wavfile import read as wav_read
import io
import ffmpeg

AUDIO_HTML = """
<script>
var my_div = document.createElement("DIV");
var my_p = document.createElement("P");
var my_btn = document.createElement("BUTTON");
var t = document.createTextNode("Press to start recording");

my_btn.appendChild(t);
//my_p.appendChild(my_btn);
my_div.appendChild(my_btn);
document.body.appendChild(my_div);

var base64data = 0;
var reader;
var recorder, gumStream;
var recordButton = my_btn;

var handleSuccess = function(stream) {
  gumStream = stream;
  var options = {
    //bitsPerSecond: 8000, //chrome seems to ignore, always 48k
    mimeType : 'audio/webm;codecs=opus'
    //mimeType : 'audio/webm;codecs=pcm'
  };
  //recorder = new MediaRecorder(stream, options);
  recorder = new MediaRecorder(stream);
  recorder.ondataavailable = function(e) {
    var url = URL.createObjectURL(e.data);
    var preview = document.createElement('audio');
    preview.controls = true;
    preview.src = url;
    document.body.appendChild(preview);

    reader = new FileReader();
    reader.readAsDataURL(e.data);
    reader.onloadend = function() {
      base64data = reader.result;
      //console.log("Inside FileReader:" + base64data);
    }
  };
  recorder.start();
  };

recordButton.innerText = "Recording... press to stop";

navigator.mediaDevices.getUserMedia({audio: true}).then(handleSuccess);


function toggleRecording() {
  if (recorder && recorder.state == "recording") {
      recorder.stop();
      gumStream.getAudioTracks()[0].stop();
      recordButton.innerText = "Saving the recording... pls wait!"
  }
}

// https://stackoverflow.com/a/951057
function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

var data = new Promise(resolve=>{
//recordButton.addEventListener("click", toggleRecording);
recordButton.onclick = ()=>{
toggleRecording()

sleep(2000).then(() => {
  // wait 2000ms for the data to be available...
  // ideally this should use something like await...
  //console.log("Inside data:" + base64data)
  resolve(base64data.toString())

});

}
});

</script>
"""

# %cd /
from ghc.l_ghc_cf import l_ghc_cf
# %cd content

def get_audio():
  display(HTML(AUDIO_HTML))
  data = eval_js("data")
  binary = b64decode(data.split(',')[1])

  process = (ffmpeg
    .input('pipe:0')
    .output('pipe:1', format='wav')
    .run_async(pipe_stdin=True, pipe_stdout=True, pipe_stderr=True, quiet=True, overwrite_output=True)
  )
  output, err = process.communicate(input=binary)

  riff_chunk_size = len(output) - 8
  # Break up the chunk size into four bytes, held in b.
  q = riff_chunk_size
  b = []
  for i in range(4):
      q, r = divmod(q, 256)
      b.append(r)

  # Replace bytes 4:8 in proc.stdout with the actual size of the RIFF chunk.
  riff = output[:4] + bytes(b) + output[8:]

  sr, audio = wav_read(io.BytesIO(riff))

  return audio, sr


from IPython.display import HTML
from base64 import b64encode
def showVideo(path):
  mp4 = open(str(path),'rb').read()
  data_url = "data:video/mp4;base64," + b64encode(mp4).decode()
  return HTML("""
  <video width=700 controls>
        <source src="%s" type="video/mp4">
  </video>
  """ % data_url)

from IPython.display import clear_output

#@title STEP2: Select a Youtube Video
# Install yt-dlp

import os
!pip install yt-dlp

!rm -df youtube.mp4

#@markdown ___
from urllib import parse as urlparse
YOUTUBE_URL = 'https://www.youtube.com/watch?v=YMuuEv37s0o' #@param {type:"string"}
url_data = urlparse.urlparse(YOUTUBE_URL)
query = urlparse.parse_qs(url_data.query)
YOUTUBE_ID = query["v"][0]


# remove previous input video
!rm -f /content/sample_data/input_vid.mp4


#@markdown ___

#@markdown ### Trim the video (start, end) seconds
start = 0 #@param {type:"integer"}
end = 8 #@param {type:"integer"}
interval = end - start

#@markdown <font color="orange"> Note: ``the trimmed video must have face on all frames``

# Download the YouTube video using yt-dlp
!yt-dlp -f 'bestvideo[ext=mp4]' --output "youtube.%(ext)s" https://www.youtube.com/watch?v=$YOUTUBE_ID

# Cut the video using FFmpeg
!ffmpeg -y -i youtube.mp4 -ss {start} -t {interval} -async 1 /content/sample_data/input_vid.mp4

# Preview the trimmed video
from IPython.display import HTML
from base64 import b64encode
mp4 = open('/content/sample_data/input_vid.mp4','rb').read()
data_url = "data:video/mp4;base64," + b64encode(mp4).decode()
HTML(f"""<video width=600 controls><source src="{data_url}"></video>""")

#@title STEP3: Select Audio (Record, Upload from local drive or Gdrive)
import os
from IPython.display import Audio
from IPython.core.display import display

upload_method = 'Upload' #@param ['Record', 'Upload', 'Custom Path']

#remove previous input audio
if os.path.isfile('/content/sample_data/input_audio.wav'):
    os.remove('/content/sample_data/input_audio.wav')

def displayAudio():
  display(Audio('/content/sample_data/input_audio.wav'))

if upload_method == 'Record':
  audio, sr = get_audio()
  import scipy
  scipy.io.wavfile.write('/content/sample_data/input_audio.wav', sr, audio)

elif upload_method == 'Upload':
  from google.colab import files
  uploaded = files.upload()
  for fn in uploaded.keys():
    print('User uploaded file "{name}" with length {length} bytes'.format(
        name=fn, length=len(uploaded[fn])))

  # Consider only the first file
  PATH_TO_YOUR_AUDIO = str(list(uploaded.keys())[0])

  # Load audio with specified sampling rate
  import librosa
  audio, sr = librosa.load(PATH_TO_YOUR_AUDIO, sr=None)

  # Save audio with specified sampling rate
  import soundfile as sf
  sf.write('/content/sample_data/input_audio.wav', audio, sr, format='wav')

  clear_output()
  displayAudio()

elif upload_method == 'Custom Path':
  from google.colab import drive
  drive.mount('/content/drive')
  #@markdown ``Add the full path to your audio on your Gdrive`` 👇
  PATH_TO_YOUR_AUDIO = '/content/8.wav' #@param {type:"string"}

  # Load audio with specified sampling rate
  import librosa
  audio, sr = librosa.load(PATH_TO_YOUR_AUDIO, sr=None)

  # Save audio with specified sampling rate
  import soundfile as sf
  sf.write('/content/sample_data/input_audio.wav', audio, sr, format='wav')

  clear_output()
  displayAudio()

#@title STEP4: Start Crunching and Preview Output
#@markdown <b>Note: Only change these, if you have to</b>
pad_top =  0#@param {type:"integer"}
pad_bottom =  16#@param {type:"integer"}
pad_left =  2#@param {type:"integer"}
pad_right =  2#@param {type:"integer"}
rescaleFactor =  2#@param {type:"integer"}
nosmooth = False #@param {type:"boolean"}

if nosmooth == False:
  !cd Wav2Lip && python inference.py --checkpoint_path checkpoints/wav2lip_gan.pth --face "../sample_data/input_vid.mp4" --audio "../sample_data/input_audio.wav" --pads $pad_top $pad_bottom $pad_left $pad_right --resize_factor $rescaleFactor
else:
  !cd Wav2Lip && python inference.py --checkpoint_path checkpoints/wav2lip_gan.pth --face "../sample_data/input_vid.mp4" --audio "../sample_data/input_audio.wav" --pads $pad_top $pad_bottom $pad_left $pad_right --resize_factor $rescaleFactor --nosmooth

#Preview output video
clear_output()
print("Final Video Preview")
print("Download this video from", '/content/Wav2Lip/results/result_voice.mp4')
showVideo('/content/Wav2Lip/results/result_voice.mp4')

!pwd

!git clone https://github.com/joonson/syncnet_python.git

cd syncnet_python/

!pip install -r requirements.txt
!sh download_model.sh

"""Running the evaluation scripts:"""

cd /content/Wav2Lip/evaluation/scores_LSE/

!cp *.py /content/syncnet_python/

!cp *.sh /content/syncnet_python/

mkdir video-data_root

cd syncnet_python

cd syncnet_python

sh calculate_scores_real_videos.sh /path/to/video/data/root
