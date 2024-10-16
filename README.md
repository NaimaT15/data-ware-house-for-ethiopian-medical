## Object Detection, FastAPI Exposure, and Data Pipeline for Ethiopian Medical Businesses 👋
## Overview
This project focuses on developing a robust system for object detection, data exposure via a FastAPI
service, and a data pipeline that handles scraping, collection, cleaning, and transformation of data for 
Ethiopian medical businesses.

## Key Features:
- **Object Detection:** Using YOLOv5 for detecting objects from images collected through different channels.
- **FastAPI Integration:** Exposing collected data through RESTful APIs for efficient retrieval and management.
- **Data Pipeline:** Includes scraping, collection, and processing of raw data to make it ready for analytics and usage.
- **Data Cleaning & Transformation:** Cleaning the collected data and transforming it into a structured format for further analysis.

## Setup Instructions
**1. Clone the Repository**
```bash
git clone <repository-url>
cd my_project
```
**2. Install Dependencies**
```bash
pip install -r requirements.txt
```
**3. Set Up Environment Variables**

Create a .env file in the root directory and add your database configuration:
```bash
makefile
DB_URL=<your-database-url>
```

**4. Start the FastAPI Server**
```bash
uvicorn my_fastapi.main:app --reload
```
Access the FastAPI docs at http://127.0.0.1:8000/docs.

## Sample API Endpoints
**1. Retrieve Detection Results**
```bash
GET /detection-results/?skip=0&limit=10
```
**2. Create New Detection Result**
```bash
POST /detection-results/
```
**3. Update a Detection Result**
```bash

PUT /detection-results/{id}
```
**4. Delete a Detection Result**
```bash

DELETE /detection-results/{id}
```
## Contributing

Contributions are welcome! Please fork this repository and submit a pull request with your changes.

## Acknowledgements
- **10 Academy:** For providing the challenge.

## Contribution
Contributions are welcome! Please create a pull request or issue to suggest improvements or add new features.


## Author

👤 **Naima Tilahun**

* Github: [@NaimaT15](https://github.com/NaimaT15)
