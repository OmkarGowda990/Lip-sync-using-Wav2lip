# Lip-sync-using-Wav2lip

To achieve the output we have used the pre-trained model from Wav2Lip, more specifically the Wav2Lip + GAN model, the GitHub page for which can be found [here](https://github.com/Rudrabha/Wav2Lip).

## Steps to run
1. Clone the repository `git clone https://github.com/OmkarGowda990/Lip-sync-using-Wav2lip.git`

2. Open the **LipSync.ipynb** file in your Google colab and upload the **inference_gfpgan.py** files in the base directory ie. `/content/` 
> The script will itself place them in their required directories.

3. Make sure to update the inference.py file to ensure frame skipping for no face detection.

4. Connect to the drive and upload your audio and video to the `/content/wav2lip-HD/inputs` directory.
   
5. Connect your colab notebook to the runtime and run all.
  
7. Choose your Wav2Lip model. 

8. Run all the below cells till ***Adding audio to GAN output*** section. Your video will be downloaded!


## Colab:
The final Google Colab notebook after solving all of the above problems can be found [here](https://colab.research.google.com/drive/11Ik6RS80jY8zlLd7bdtfyv0kGVTB7Rlc?usp=sharing)

