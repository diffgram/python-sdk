## Description

This is a simple script to import [EPRI Distribution Inspection Imagery](https://www.kaggle.com/datasets/dexterlewis/epri-distribution-inspection-imagery) to Diffgram

So far we, it only imports annotation with type **polygon** and skips annotations with type **line** (polyline type of instance doesn't exist on Diffgram yet), but that will be improved in future version

## Usage

1. Create and activate virtual environment

```
virtualenv your-env-name
source your-env-name/bin/activate
```

2. Install dependencies from **requirements.txt**:

```
pip install -r requirements.txt
```

3. Download [annotations file](https://publicstorageaccnt.blob.core.windows.net/drone-distribution-inspection-imagery/Overhead-Distribution-Labels.csv) and place it to the root folder

4. Download images and unzip them to **images** folder

5. Create .env file and set environmental variables:

```
touch .env
```

```
PROJECT_STRING_ID=project-string-id
CLIENT_ID=client-id
CLIENT_SECRET=client-secret
HOST=https://example.com
```

6. Run script:

```
python import.py
```