import os
import asyncio
import logging
import httpx
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

load_dotenv()


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
PERPLEXITY_API_KEY = os.environ.get("PERPLEXITY_API_KEY")


PERPLEXITY_API_URL = "https://api.perplexity.ai/chat/completions"
PERPLEXITY_MODEL = "sonar-pro"  

PROMPT_TEMPLATE = """You are a supportive parenting advisor called BabyAdvisor. You provide evidence-based, empathetic advice to parents with young children.

IMPORTANT GUIDELINES:
- Offer practical, research-backed information on common parenting challenges 
- Be empathetic and understanding of parenting struggles
- Provide emotional support and reassurance
- NEVER give medical diagnosis or specific medical treatment recommendations
- Always suggest consulting a healthcare provider for medical concerns
- Focus on general best practices and child development information
- Keep responses concise, warm, and helpful
- Acknowledge the challenges of parenting

User's parenting question or concern: {user_query}

Please provide helpful, supportive advice:"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a welcome message when the command /start is issued."""
    user = update.effective_user
    welcome_message = (
        f"👋 Hi {user.first_name}! I'm BabyAdvisor, your parenting support bot.\n\n"
        f"I can provide evidence-based advice for common parenting challenges.\n\n"
        f"To ask me anything, just use the /baby command followed by your question.\n\n"
        f"For example: /baby My 3-month-old isn't sleeping well at night\n\n"
        f"Remember: I'm not a substitute for professional medical advice. "
        f"Always consult with healthcare providers for medical concerns."
    )
    await update.message.reply_text(welcome_message)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a help message when the command /help is issued."""
    help_text = (
        "🤱 *BabyAdvisor Help*\n\n"
        "*Commands:*\n"
        "/start - Welcome message and bot introduction\n"
        "/help - Show this help message\n"
        "/baby [your question] - Ask for parenting advice\n\n"
        "*Examples:*\n"
        "/baby My 6-month-old refuses solid foods\n"
        "/baby How to handle toddler tantrums\n"
        "/baby When should my baby start crawling?\n\n"
        "Remember that I provide general advice, not medical diagnosis. "
        "Always consult healthcare professionals for medical concerns."
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")

async def query_perplexity_api(query_text: str) -> str:
    """Query the Perplexity API with the user's parenting question."""
    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json"
    }
    
    formatted_prompt = PROMPT_TEMPLATE.format(user_query=query_text)
    
    payload = {
        "model": PERPLEXITY_MODEL,
        "messages": [
            {"role": "system", "content": "You are a parenting advisor providing evidence-based, empathetic advice."},
            {"role": "user", "content": formatted_prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 500
    }
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(PERPLEXITY_API_URL, json=payload, headers=headers)
            response.raise_for_status()
            response_data = response.json()
            return response_data["choices"][0]["message"]["content"]
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error occurred when calling Perplexity API: {e}")
        return "Sorry, I couldn't get advice at the moment. Please try again later."
    except httpx.RequestError as e:
        logger.error(f"Network error occurred when calling Perplexity API: {e}")
        return "Sorry, I'm having trouble connecting to my knowledge source. Please try again later."
    except Exception as e:
        logger.error(f"Unexpected error when calling Perplexity API: {e}")
        return "Sorry, something went wrong. Please try again later."

async def baby_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /baby command - query Perplexity for parenting advice."""
    user_query = " ".join(context.args)
    
    if not user_query:
        await update.message.reply_text(
            "Please include your parenting question after the /baby command.\n"
            "For example: /baby My 2-month-old is spitting up a lot"
        )
        return
    
    
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    processing_message = await update.message.reply_text(
        "I'm thinking about your question, please wait a moment..."
    )
    
  
    try:
        response_text = await query_perplexity_api(user_query)
        await processing_message.delete()
        
  
        await update.message.reply_text(response_text)
    except Exception as e:
        logger.error(f"Error processing baby command: {e}")
        await update.message.reply_text(
            "Sorry, I had trouble processing your question. Please try again later."
        )

async def handle_unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle unknown commands."""
    await update.message.reply_text(
        "Sorry, I didn't understand that command. Use /help to see available commands."
    )

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle regular text messages - prompt to use the /baby command."""
    await update.message.reply_text(
        "To ask a parenting question, please use the /baby command followed by your question.\n"
        "For example: /baby My baby won't sleep through the night"
    )

def main() -> None:
    """Start the bot."""
    if not TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN environment variable is not set.")
        return
    
    if not PERPLEXITY_API_KEY:
        logger.error("PERPLEXITY_API_KEY environment variable is not set.")
        return
    
    
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("baby", baby_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    

    application.add_handler(MessageHandler(filters.COMMAND, handle_unknown_command))

  
    logger.info("Starting BabyAdvisor bot...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()