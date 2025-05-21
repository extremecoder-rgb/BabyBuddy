# BabyAdvisor Telegram Bot

BabyAdvisor is a Telegram bot designed to provide evidence-based parenting advice and support. It helps parents get quick, reliable answers to common parenting questions and challenges.

## Features

- Evidence-based parenting advice
- Easy-to-use command interface
- Quick responses to common parenting questions
- Safe and informative guidance

## Prerequisites

- Python 3.7 or higher
- Telegram Bot Token (from [@BotFather](https://t.me/botfather))
- Perplexity API Key

## Installation

1. Clone the repository or download the source code

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project root and add your API keys:
```
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
PERPLEXITY_API_KEY=your_perplexity_api_key
```

## Usage

Start the bot by running:
```bash
python app.py
```

### Available Commands

- `/start` - Get a welcome message and introduction to the bot
- `/help` - Display help information and usage examples
- `/baby [question]` - Ask a parenting-related question

### Example Questions

- `/baby My 6-month-old refuses solid foods`
- `/baby How to handle toddler tantrums`
- `/baby When should my baby start crawling?`

## Important Note

This bot provides general parenting advice and is not a substitute for professional medical consultation. Always consult healthcare providers for medical concerns.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.