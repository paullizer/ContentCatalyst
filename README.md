# ContentCatalyst

ContentCatalyst is an all-in-one content enhancement tool designed to streamline the workflow of journalists and content creators. Leverage the power of AI to generate engaging titles, craft compelling introductions and summaries, optimize content for SEO, create SEO-friendly tags, and translate articles into multiple languages seamlessly.

## Table of Contents

- [Features](#features)
- [Demo](#demo)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Technologies Used](#technologies-used)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgments](#acknowledgments)

## Features

1. **Article Titles**
   - Generate captivating and SEO-friendly titles to grab your readers' attention.
2. **Introductions & Summaries**
   - Craft compelling introductions and concise summaries tailored to your audience.
3. **Automated SEO Text**
   - Generate SEO-optimized titles and introductions to boost your content's visibility.
4. **SEO-Friendly Tags**
   - Automatically generate relevant tags to improve your content's searchability.
5. **Article Translation**
   - Translate your articles seamlessly into multiple languages. *Note: This feature requires uploading a TXT, MD, or DOCX file.*

## Demo

![Demo Screenshot](static/demo.png)

## Installation

### Prerequisites

- **Python 3.7 or higher**
- **pip** (Python package installer)
- **Git** (for cloning the repository)

### Steps

1. **Clone the Repository**

   ```bash
   git clone https://github.com/yourusername/ContentCatalyst.git
   cd ContentCatalyst
   ```

2. **Create a Virtual Environment**

   It's recommended to use a virtual environment to manage dependencies.

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up Environment Variables**

   Create a `.env` file in the root directory and add the following variables:

   ```env
   FLASK_KEY=your_flask_secret_key
   AZURE_OPENAI_API_TYPE=azure
   AZURE_OPENAI_ENDPOINT=https://your-azure-openai-endpoint/
   AZURE_OPENAI_API_VERSION=2023-05-15
   AZURE_OPENAI_KEY=your_azure_openai_key
   AZURE_OPENAI_MODEL=your_deployment_name
   AZURE_TRANSLATION_ENDPOINT=https://api.cognitive.microsofttranslator.com/translate
   AZURE_TRANSLATION_KEY=your_translation_subscription_key
   AZURE_TRANSLATION_REGION=your_translation_service_region
   AZURE_TRANSLATION_LANGUAGE_URL=https://api.cognitive.microsofttranslator.com/languages?api-version=3.0
   ```

   **Note:**
   - Replace placeholders (e.g., `your_flask_secret_key`, `your_azure_openai_key`) with your actual credentials.
   - Ensure that the `.env` file is **not** committed to version control for security reasons.

5. **Activate Environment Variables**

   Use `python-dotenv` to load environment variables. Ensure it's installed by checking `requirements.txt`.

   ```bash
   # If not already installed
   pip install python-dotenv
   ```

   Then, ensure your `app.py` loads the `.env` file:

   ```python
   from dotenv import load_dotenv
   load_dotenv()
   ```

6. **Run the Application**

   ```bash
   python app.py
   ```

   The application will be accessible at `http://127.0.0.1:5000/`.

## Configuration

### Environment Variables

Ensure all the necessary environment variables are set, either through a `.env` file or your deployment environment.

- **Flask Configuration:**
  - `FLASK_KEY`: Secret key for Flask sessions.

- **Azure OpenAI Configuration:**
  - `AZURE_OPENAI_API_TYPE`: API type (e.g., "azure").
  - `AZURE_OPENAI_ENDPOINT`: Your Azure OpenAI endpoint URL.
  - `AZURE_OPENAI_API_VERSION`: API version (e.g., "2023-05-15").
  - `AZURE_OPENAI_KEY`: Subscription key for Azure OpenAI.
  - `AZURE_OPENAI_MODEL`: Deployment name or model identifier.

- **Azure Translation Service Configuration:**
  - `AZURE_TRANSLATION_ENDPOINT`: Endpoint URL for the Translator Text API.
  - `AZURE_TRANSLATION_KEY`: Subscription key for the Translator Text API.
  - `AZURE_TRANSLATION_REGION`: Region of your Translator Text API service.
  - `AZURE_TRANSLATION_LANGUAGE_URL`: URL to fetch supported languages (e.g., `https://api.cognitive.microsofttranslator.com/languages?api-version=3.0`).

### Allowed File Types

The application allows uploading the following file types for translation:

- `.txt`
- `.md`
- `.docx`

Ensure that uploaded files adhere to these formats.

## Usage

1. **Home Page**

   - Visit `http://127.0.0.1:5000/` to access the home page.
   - Select the desired features by checking the corresponding boxes.
   - Click the **Next** button to proceed.

2. **Choose Content Input Method**

   - Depending on your feature selections, choose how to provide your content:
     - **Provide Text:** Manually enter your topic and article content.
     - **Upload Content:** Upload a TXT, MD, or DOCX file containing your article.

3. **Provide Text or Upload Content**

   - **Provide Text:**
     - Enter your topic and article content in the provided editor.
   - **Upload Content:**
     - Select a file to upload. Ensure it is in one of the allowed formats.

4. **Options Page**

   - Configure additional settings based on selected features.
   - For **Article Translation**, select target languages.
   - Click the **Generate Content** button to process.

5. **Results Page**

   - View the generated content, including translations if applicable.
   - Use the **Copy** buttons to easily copy translations.

## Technologies Used

- **Backend:**
  - [Flask](https://flask.palletsprojects.com/): Web framework for Python.
  - [OpenAI API](https://openai.com/api/): For generating content.
  - [Microsoft Translator Text API](https://azure.microsoft.com/en-us/services/cognitive-services/translator-text-api/): For translating content.
  - [docx2txt](https://pypi.org/project/docx2txt/): To extract text from DOCX files.
  - [requests](https://docs.python-requests.org/): For making HTTP requests.

- **Frontend:**
  - [Bootstrap 5](https://getbootstrap.com/): CSS framework for responsive design.
  - [JavaScript](https://developer.mozilla.org/en-US/docs/Web/JavaScript): For dynamic UI interactions.

- **Utilities:**
  - [python-dotenv](https://pypi.org/project/python-dotenv/): To manage environment variables.
  - [markdown](https://pypi.org/project/Markdown/): To render Markdown content.
  - [bleach](https://pypi.org/project/bleach/): To sanitize HTML content.

## Contributing

Contributions are welcome!

## License

This project is licensed under the [MIT License](LICENSE).

## Acknowledgments

- [OpenAI](https://openai.com/) for providing powerful AI models.
- [Microsoft Azure](https://azure.microsoft.com/) for the Translator Text API.
- [Bootstrap](https://getbootstrap.com/) for the responsive UI framework.
- [Flask](https://flask.palletsprojects.com/) for the web framework.
- [docx2txt](https://pypi.org/project/docx2txt/) for handling DOCX files.

---

*Feel free to reach out or open an issue if you encounter any problems or have suggestions for improvements!*

---