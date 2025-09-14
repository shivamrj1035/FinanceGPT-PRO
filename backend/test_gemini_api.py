#!/usr/bin/env python
"""
Test Gemini API Key with the correct format
"""

import os
from google import genai
from google.genai import types

def test_gemini_api():
    """
    Test if Gemini API key is working using the correct format
    """
    # Your API key
    api_key = "AIzaSyArVob6IeFoZjRIRe5aQuivtXjkSn9iMV8"

    print("🔍 Testing Gemini API Key...")
    print(f"API Key: {api_key[:10]}...{api_key[-4:]}")

    try:
        # Initialize client with your API key
        client = genai.Client(api_key=api_key)

        # Use the model you specified
        model = "gemini-2.0-flash-exp"  # Using stable model version

        # Create test content
        contents = [
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(text="Say 'Hello, FinanceGPT Pro is ready!' if you can read this."),
                ],
            ),
        ]

        # Configuration without thinking_config (for compatibility)
        generate_content_config = types.GenerateContentConfig(
            temperature=0.7,
            top_p=0.95,
            top_k=40,
            max_output_tokens=100,
        )

        print("\n📤 Sending test request to Gemini API...")

        # Test with streaming
        response_text = ""
        for chunk in client.models.generate_content_stream(
            model=model,
            contents=contents,
            config=generate_content_config,
        ):
            if chunk.text:
                response_text += chunk.text
                print(chunk.text, end="")

        if response_text:
            print("\n\n✅ SUCCESS! Your Gemini API key is working!")

            # Test a financial question
            print("\n📤 Testing financial question...")

            financial_contents = [
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_text(text="What is compound interest in one sentence?"),
                    ],
                ),
            ]

            response_text = ""
            for chunk in client.models.generate_content_stream(
                model=model,
                contents=financial_contents,
                config=generate_content_config,
            ):
                if chunk.text:
                    response_text += chunk.text
                    print(chunk.text, end="")

            print("\n\n🎉 All tests passed! Your API key is valid and working!")
            print("✅ You can use this API key for FinanceGPT Pro!")
            return True
        else:
            print("\n⚠️ No response received from API")
            return False

    except Exception as e:
        print(f"\n❌ ERROR: API key test failed!")
        print(f"Error type: {type(e).__name__}")
        print(f"Error details: {str(e)}")

        if "API_KEY_INVALID" in str(e) or "401" in str(e):
            print("\n⚠️ The API key appears to be invalid or not authorized.")
            print("Please check:")
            print("1. The API key is copied correctly")
            print("2. The API key is activated in Google AI Studio")
            print("3. Gemini API is enabled for your project")
        elif "QUOTA" in str(e) or "429" in str(e):
            print("\n⚠️ API quota exceeded or rate limited.")
            print("Wait a few minutes and try again.")
        elif "404" in str(e):
            print("\n⚠️ Model not found. The API might be using a different model version.")
        else:
            print("\n⚠️ Connection or configuration issue.")
            print("Possible solutions:")
            print("1. Check your internet connection")
            print("2. Ensure google-genai package is installed: pip install google-genai")
            print("3. Try with a different model like 'gemini-1.5-flash'")

        return False

def test_with_env_variable():
    """
    Test with environment variable
    """
    print("\n" + "="*50)
    print("Testing with environment variable...")

    # Set environment variable
    os.environ["GEMINI_API_KEY"] = "AIzaSyArVob6IeFoZjRIRe5aQuivtXjkSn9iMV8"

    try:
        client = genai.Client(
            api_key=os.environ.get("GEMINI_API_KEY"),
        )

        print("✅ Environment variable set successfully")
        print(f"API Key from env: {os.environ.get('GEMINI_API_KEY')[:10]}...")

        # Quick test
        model = "gemini-2.0-flash-exp"
        contents = [
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(text="Reply with 'OK' if working"),
                ],
            ),
        ]

        for chunk in client.models.generate_content_stream(
            model=model,
            contents=contents,
            config=types.GenerateContentConfig(max_output_tokens=10),
        ):
            if chunk.text:
                print(f"Response: {chunk.text}")
                print("✅ Environment variable method works!")
                return True

    except Exception as e:
        print(f"❌ Environment variable method failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 FinanceGPT Pro - Gemini API Key Test")
    print("="*50)

    # Test direct API key
    result1 = test_gemini_api()

    # Test with environment variable
    result2 = test_with_env_variable()

    print("\n" + "="*50)
    print("📊 Test Summary:")
    print(f"Direct API Key Test: {'✅ PASSED' if result1 else '❌ FAILED'}")
    print(f"Environment Variable Test: {'✅ PASSED' if result2 else '❌ FAILED'}")

    if result1 or result2:
        print("\n🎯 Your Gemini API key is working! You can run the backend.")
        print("\nTo use it in the project, either:")
        print("1. Set environment variable: export GEMINI_API_KEY='AIzaSyArVob6IeFoZjRIRe5aQuivtXjkSn9iMV8'")
        print("2. Add to .env file: GEMINI_API_KEY=AIzaSyArVob6IeFoZjRIRe5aQuivtXjkSn9iMV8")
    else:
        print("\n⚠️ API key is not working. Please check the error messages above.")