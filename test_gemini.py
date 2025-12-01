import google.generativeai as genai
import config

genai.configure(api_key=config.GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

try:
    response = model.generate_content('Say hello in JSON format')
    print('✅ Gemini API Test Successful!')
    print('Response:', response.text[:100])
except Exception as e:
    print(f'❌ Gemini API Test Failed: {e}')
