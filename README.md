# Virtual Fence Data Workshop

## Prerequisites

Google Account with access to Google Drive and Google Collab

## Setup

1. Install R (we're using version 4.2.2)
2. Install R Studio (we're using version 2022.12.0 Build 353)
3. Setup Google Collab and Google Drive
4. [Optional] Install Anaconda for Python


We recommend that you download this GitHub repository as a zip (compressed) folder during the workshop. Click on the green "Code" button and select "Download ZIP"  to download a local copy.

![](docs/attachments/download-repo-as-zip-folder.jpg)

## Important Links

1. [Workshop Code](https://github.com/amantaya/vf-workshop/tree/main/code)
2. [HackMD (for live coding assistance)](https://hackmd.io/@yW3saP0JQS-tB5uNp9cJ-Q/Hk7YL6Uhs/edit)
3. [Google Collab](https://colab.research.google.com/github/amantaya/vf-workshop/blob/main/code/VF_In_Service_Vence_API.ipynb)
4. [Virtual Fence Wrangling](https://github.com/Brandkmayer/VenceVFWrangling)
5. [Vence-API](https://github.com/amantaya/Vence-API)


## Understanding Virtual Fence Message Data

[Vence Data Definitions V2](https://docs.google.com/document/d/1mSkW57wWF59D9fOm_tbnTVByqaYR4UnV/edit)

## Accessing Virtual Fence Message Data with the API

APIs allow you to create, read, update, and delete data from another computer or server.

In our specific case, we can only read data from a server. The API controls access to virtual fence data through authentication. We need to supply the API with a username and password to retrieve data.

![Vence API Diagram](docs/attachments/Vence-API-Diagram.jpg)

### Retrieving Virtual Fence Message Data Through the API

We have set up a Google Collab Notebook for this workshop. Google Collab is a free service that runs Jupyter Notebooks (which are similar to R Markdown notebooks) in the cloud. This means that you run Python in the cloud, not on your local computer. This has several advantages, including not tying up your computer's resources (CPU/Memory) to run a script, and in our case, you don't have to download packages/libraries to your local computer (making workshop setup much easier!).

Open the [Google Collab](https://colab.research.google.com/github/amantaya/vf-workshop/blob/main/code/VF_In_Service_Vence_API.ipynb) notebook. You may be prompted to sign in to your Google account, if not already signed in.

You will be prompted to grant permission for the Google Collab notebook to access all files on your Google Drive.

**Note: You need to be logged into the same Google account that you are mounting the Google Drive to. If you are using Google Chrome as your web browser, make sure you are logged into Chrome with the same Google account that you will be using to store data on your Google Drive.**

**Do not  use a Google Drive that contains sensitive or personal data**, as this grants full access to all of the files in your Google Drive (see image below). You can always create another free Google account to run this analysis to avoid granting access to your personal Google Drive files. 

![Allow Access to Google Drive Prompt](docs/attachments/allow-access-to-google-drive.jpg)

![Permissions for Google Drive](docs/attachments/permission-for-google-drive.jpg)

## Managing Virtual Fence Message Data with a Database

## Creating Virtual Fences in R

[VenceVFWrangling](https://github.com/Brandkmayer/VenceVFWrangling)

## Turning Virtual Fences Message Data into DataFrames in R