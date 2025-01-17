import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
import time
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
TOKEN = os.getenv('TOKEN')
COMPANY_ID = os.getenv('COMPANY_ID')
INPUT_ID = os.getenv('INPUT_ID')
INPUT_PASSWORD = os.getenv('INPUT_PASSWORD')

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Hello! Send me /scrape to get webpage info.')

async def scrape(update: Update, context: ContextTypes.DEFAULT_TYPE):

    url = "https://portal.nueip.com/login"
    await update.message.reply_text(f'Scraping {url}...')
    
    try:
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument("--window-size=1920,1080")
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--allow-running-insecure-content')
        user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'
        options.add_argument(f'user-agent={user_agent}')
        # Use webdriver_manager to handle driver installation
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        await update.message.reply_text('Accessing webpage...')
        driver.get(url)
        

        # Wait for the page to load
        await update.message.reply_text('Page loaded, filling in credentials...')

        # Find the search bar using its name attribute
        input1 = driver.find_element(By.NAME, "inputCompany")
        input2 = driver.find_element(By.NAME, "inputID")
        input3 = driver.find_element(By.NAME, "inputPassword")

        input_company = COMPANY_ID
        input_id = INPUT_ID
        input_password = INPUT_PASSWORD

        input1.send_keys(input_company)
        input2.send_keys(input_id)
        input3.send_keys(input_password)

        await update.message.reply_text('Credentials filled, submitting...')
        submit_button = driver.find_element(By.CLASS_NAME, "login-button")
        submit_button.send_keys(Keys.RETURN)

        # Wait for the results to load
        time.sleep(5)

        title = driver.title
        
        await update.message.reply_text(f'Title: {title}')
        checkout_button = driver.find_element(By.XPATH, "//*[@id=\"view-gridlayout\"]/div[4]/div[1]/div[1]/div[2]/div/div[2]/div/div[2]/button")
        print(f'Checkout button: {checkout_button}')
        checkout_button.click()
        await update.message.reply_text('Checkout button clicked, waiting for the next step...')
        time.sleep(5)
        await update.message.reply_text('Done')
        driver.quit()
        
    except Exception as e:
        await update.message.reply_text(f'Error: {str(e)}')

def main():
    # Create application
    application = ApplicationBuilder().token(TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("scrape", scrape))
    
    # Start polling
    print("Starting bot...")
    application.run_polling()

if __name__ == "__main__":
    main()