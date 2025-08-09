import streamlit as st
import requests
import pytesseract
from PIL import Image
import io
import os

# Path to tesseract.exe (change this to where you installed Tesseract)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# API Keys
APP_ID = "b7372336" 
APP_KEY = "726c0b3d70de380a65b5a6b6be38691f	"

st.title("🍽 Food AI Assistant")
st.write("Upload a recipe image or enter ingredients to get **accurate calories, nutrition breakdown, and AI suggestions!**")

# Image Upload
uploaded_image = st.file_uploader("Upload a dish image", type=["jpg", "jpeg", "png"])

ingredients_list = []

if uploaded_image:
    image = Image.open(uploaded_image)
    st.image(image, caption="Uploaded Dish Image", use_column_width=True)

    # OCR to extract text
    ocr_text = pytesseract.image_to_string(image)
    st.write("**Detected Text from Image:**")
    st.write(ocr_text)

    # Convert OCR output to ingredient list (one per line)
    ingredients_list = [line.strip() for line in ocr_text.split("\n") if line.strip()]

# Manual ingredient input
manual_ingredients = st.text_area("Or enter ingredients (one per line):", value="\n".join(ingredients_list))

if st.button("Analyze Nutrition"):
    if manual_ingredients.strip():
        ingredient_lines = manual_ingredients.strip().split("\n")
        url = "https://api.edamam.com/api/nutrition-details"
        headers = {"Content-Type": "application/json"}
        data = {
            "title": "Recipe",
            "ingr": ingredient_lines
        }

        response = requests.post(url, headers=headers, json=data, params={"app_id": APP_ID, "app_key": APP_KEY})

        if response.status_code == 200:
            data = response.json()

            st.subheader("Ingredient Details:")
            total_calories = 0
            for item in data.get("ingredients", []):
                name = item.get("text", "Unknown ingredient")
                if item.get("parsed"):
                    nutrients = item["parsed"][0].get("nutrients", {})
                    kcal = nutrients.get("ENERC_KCAL", {}).get("quantity", 0)
                    protein = nutrients.get("PROCNT", {}).get("quantity", 0)
                    fat = nutrients.get("FAT", {}).get("quantity", 0)
                    carbs = nutrients.get("CHOCDF", {}).get("quantity", 0)

                    total_calories += kcal
                    st.write(f"- **{name}**: {round(kcal, 2)} kcal, {round(protein, 2)}g protein, {round(fat, 2)}g fat, {round(carbs, 2)}g carbs")

            st.write(f"**Total Calories:** {round(total_calories, 2)} kcal")

            st.subheader("AI Suggestions to Enhance Dish")
            st.write("✅ Add fresh herbs or spices for extra flavor.")
            st.write("✅ Try roasting or grilling for better texture.")
        else:
            st.error(f"API Error {response.status_code}: {response.text}")
    else:
        st.warning("Please enter ingredients or upload an image.")
