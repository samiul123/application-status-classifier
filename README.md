# application-status-classifier

Applying for jobs is a rigorous process; it is more like a full-time job. While it is necessary to track the applications, sometimes it is challenging to do so. Many web applications are developed to serve this purpose, helping to put the details when applying for the job. However, they don’t have any automated system to update the status of the job afterward. So, I thought, what if there is a system that can automatically identify the job application emails and find out their status? In which stages is that application, like Interview, Offer, or Rejection? To make it more interesting, I want to classify the sub-stages of every broad category mentioned above. For the interview, it can be an online assessment, technical, behavioral, onsite, or HR; for the offer, it can be an initial offer, negotiation, final offer, or offer follow-up; and lastly, for rejection, it can be generic rejection, feedback, rejection after an interview, position filled, etc. This classifier will take the email body as input and classify it hierarchically (like Interview->Technical).


### Environment setup

Install python==3.11.5, pip==24.3.1

Install pipenv, install requirements and activate the environment
```bash
pip install pipenv
pipenv install -r requirements.txt
pipenv shell
```

### Data Collection
To collect the data from Gmail service, use *data-collection/data-collection.py* file. But first, you need to enable Gmail API service in Google Cloud Console and create credentials.

Key datasets used for this project can be found [here](https://drive.google.com/drive/folders/1TDgUNMe0wJP_llhUnvxLjkygMu3ffiav?usp=sharing).

This external dataset of non-job related emails was used from [here](https://www.kaggle.com/datasets/dipankarsrirag/topic-modelling-on-emails).

### Notebook
To run the notebook, create *model* and *data* directory. Then, you have to place the csv files from the dataset link inside the *data* directory.