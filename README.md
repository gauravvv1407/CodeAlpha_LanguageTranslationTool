# LinguaBridge - Language Translation Tool

Created by Gaurav Kumar for the CodeAlpha Artificial Intelligence internship.

## About

A Python and Streamlit interface that sends short text to the MyMemory
translation API, then displays the translated response. This is an API-based
translation application; it does not train its own AI model.

## Features

- Source and target language selection across 15 languages.
- Short passages of up to 120 Unicode characters.
- Side-by-side input and translation panels.
- Swap language selections, clear input, and load example sentences.
- Copy via the translation box's copy icon and download UTF-8 text.
- Last five translations saved in the current browser session.
- Validation for empty input, service errors, timeouts, and usage limits.
- Clear notice when the displayed result belongs to a previous input.
- Same-language selections return the original text without an API request.

## Windows setup

1. Extract this project folder to your Desktop.
2. In VS Code, select **File > Open Folder** and open this folder. Ensure that
   `app.py` and `requirements.txt` are directly inside the opened folder.
3. Select **Terminal > New Terminal**.
4. Install the dependencies:

   ```powershell
   python -m pip install -r requirements.txt
   ```

5. Start the app:

   ```powershell
   python -m streamlit run app.py --server.port 8502
   ```

6. Open `http://localhost:8502`, or the Local URL printed in the terminal.
7. Choose source and target languages, enter a short sentence, and press
   **Translate**.

Port 8502 allows this project to run alongside your FAQ chatbot on port 8501.
Keep its terminal running while using the app. Press **Ctrl + C** to stop it.
Start the app with the terminal command, rather than VS Code's Run Python File
button, which launches it without Streamlit's application server.

If your terminal does not recognize `python`, try `py` instead. If necessary,
use your installed interpreter explicitly in PowerShell:

```powershell
& "C:\Users\HP\AppData\Local\Python\pythoncore-3.14-64\python.exe" -m streamlit run app.py --server.port 8502
```

## How translation works

The code reads the language selectors and text, then makes an HTTPS GET request
to `https://api.mymemory.translated.net/get`. The request includes `q` (the text),
`langpair` (such as `en|hi`), and `mt=1` (machine translation enabled).

The app validates the JSON response and extracts the translated text. When a
translation-memory entry has the exact source text and a higher similarity score
than the main response, the app uses that stronger entry. These scores indicate
matching similarity, not factual correctness or translation accuracy.

The API accepts at most 500 UTF-8 bytes per request. The app limits input to
120 Unicode characters, which fits that limit even for 4-byte characters.
Python's standard library handles the HTTP request, so Streamlit is the only
third-party dependency. No API key is configured in this demo.

## Limitations and data handling

- Internet access and provider availability are required for translation.
- Anonymous service usage is limited; quotas can change. See the provider's
  usage-limit documentation for current conditions.
- The provider combines public translation-memory entries and machine
  translations. It can return inaccurate or irrelevant results, particularly
  for very short or ambiguous text. Review every result before relying on it.
- Languages in the selector are requested using their language codes; actual
  support and translation quality depend on the provider.
- Text is sent to MyMemory only when **Translate** is selected.
- History stays in Streamlit session state and may disappear on a browser
  refresh or a new session. The app does not write a translation database.
- Swapping languages changes the selectors and clears the old result; it does
  not automatically translate or change the source text.
- Text-to-speech is not included; it is optional in the internship task.

## Test checklist

1. English to Hindi: `Hello! How are you today?`
2. English to French: `Where is the nearest train station?`
3. Hindi to English: `आप कैसे हैं?`
4. Select identical languages and check that text stays unchanged.
5. Submit blank input and check the validation message.
6. Change the input after translating and check the update notice.
7. Try the copy icon, text download, swap button, examples, and clear button.
8. Disconnect the internet and check the connection error, then reconnect.

Exact wording varies with the API; a successful request alone does not prove
that the translation is semantically correct.

## GitHub and submission

Create a repository named **CodeAlpha_LanguageTranslationTool**. Upload `app.py`,
`requirements.txt`, and `README.md`. The optional `.streamlit/config.toml`
file sets the intended light theme.

Record a demo showing the selectors, two translations, validation, and download.
Explain that the app sends text to an API and displays its returned translation.
Follow your CodeAlpha task sheet for LinkedIn and submission-form instructions.

## Documentation

- [MyMemory API specification](https://mymemory.translated.net/doc/spec.php)
- [MyMemory usage limits](https://mymemory.translated.net/doc/usagelimits.php)
- [Streamlit documentation](https://docs.streamlit.io/)
