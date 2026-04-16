"""
Example usage of the LLM service.

This script demonstrates how to use the LLM service for:
- Health checks
- Listing available models
- Non-streaming text generation
- Streaming text generation
- Using different explanation modes
- Error handling

Prerequisites:
- Ollama must be running (default: http://localhost:11434)
- At least one model must be pulled (e.g., ollama pull codellama:7b)

Usage:
    python examples/llm_service_example.py
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.llm_service import (
    ExplanationMode,
    LLMService,
    OllamaConnectionError,
    OllamaError,
)


async def example_health_check():
    """Example: Check if Ollama is available."""
    print("\n" + "=" * 80)
    print("Example 1: Health Check")
    print("=" * 80)
    
    service = LLMService()
    
    try:
        is_healthy = await service.health_check()
        if is_healthy:
            print("✓ Ollama is available and responding")
        else:
            print("✗ Ollama is not available")
    finally:
        await service.close()


async def example_list_models():
    """Example: List available models."""
    print("\n" + "=" * 80)
    print("Example 2: List Available Models")
    print("=" * 80)
    
    service = LLMService()
    
    try:
        models = await service.list_models()
        print(f"\nFound {len(models)} available models:\n")
        
        for model in models:
            size_gb = model.size / (1024 ** 3)
            print(f"  • {model.name}")
            print(f"    Size: {size_gb:.2f} GB")
            print(f"    Modified: {model.modified_at}")
            print()
    except OllamaError as e:
        print(f"✗ Error listing models: {e}")
    finally:
        await service.close()


async def example_basic_generation():
    """Example: Basic text generation."""
    print("\n" + "=" * 80)
    print("Example 3: Basic Text Generation")
    print("=" * 80)
    
    service = LLMService()
    
    try:
        prompt = "Explain what a Python decorator is in one sentence."
        print(f"\nPrompt: {prompt}\n")
        
        response = await service.generate(
            prompt=prompt,
            temperature=0.7,
        )
        
        print(f"Response: {response}\n")
    except OllamaConnectionError as e:
        print(f"✗ Connection error: {e}")
    except OllamaError as e:
        print(f"✗ Generation error: {e}")
    finally:
        await service.close()


async def example_explanation_modes():
    """Example: Using different explanation modes."""
    print("\n" + "=" * 80)
    print("Example 4: Explanation Modes")
    print("=" * 80)
    
    service = LLMService()
    
    code = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
"""
    
    question = "What does this function do?"
    
    try:
        # Beginner mode
        print("\n--- Beginner Mode ---\n")
        response = await service.generate_code_explanation(
            code=code,
            question=question,
            explanation_mode=ExplanationMode.BEGINNER,
            max_tokens=200,
        )
        print(response)
        
        # Technical mode
        print("\n--- Technical Mode ---\n")
        response = await service.generate_code_explanation(
            code=code,
            question=question,
            explanation_mode=ExplanationMode.TECHNICAL,
            max_tokens=200,
        )
        print(response)
        
    except OllamaError as e:
        print(f"✗ Error: {e}")
    finally:
        await service.close()


async def example_streaming_generation():
    """Example: Streaming text generation."""
    print("\n" + "=" * 80)
    print("Example 5: Streaming Generation")
    print("=" * 80)
    
    service = LLMService()
    
    try:
        prompt = "Write a short Python function to reverse a string."
        print(f"\nPrompt: {prompt}\n")
        print("Response (streaming): ", end="", flush=True)
        
        async for chunk in service.generate_stream(
            prompt=prompt,
            temperature=0.7,
            max_tokens=200,
        ):
            print(chunk, end="", flush=True)
        
        print("\n")
    except OllamaError as e:
        print(f"\n✗ Error: {e}")
    finally:
        await service.close()


async def example_custom_system_prompt():
    """Example: Using a custom system prompt."""
    print("\n" + "=" * 80)
    print("Example 6: Custom System Prompt")
    print("=" * 80)
    
    service = LLMService()
    
    try:
        custom_prompt = (
            "You are a pirate who explains code. "
            "Use pirate language and nautical metaphors."
        )
        
        prompt = "What is a Python list?"
        print(f"\nPrompt: {prompt}")
        print(f"System Prompt: {custom_prompt}\n")
        
        response = await service.generate(
            prompt=prompt,
            system_prompt=custom_prompt,
            temperature=0.9,
            max_tokens=150,
        )
        
        print(f"Response: {response}\n")
    except OllamaError as e:
        print(f"✗ Error: {e}")
    finally:
        await service.close()


async def example_error_handling():
    """Example: Error handling."""
    print("\n" + "=" * 80)
    print("Example 7: Error Handling")
    print("=" * 80)
    
    service = LLMService()
    
    try:
        # Try to use a non-existent model
        print("\nAttempting to use non-existent model...\n")
        
        response = await service.generate(
            prompt="Test prompt",
            model="nonexistent-model:1b",
        )
        
        print(f"Response: {response}")
    except OllamaConnectionError as e:
        print(f"✗ Connection Error: {e}")
    except OllamaError as e:
        print(f"✗ Expected Error: {e}")
    finally:
        await service.close()


async def main():
    """Run all examples."""
    print("\n" + "=" * 80)
    print("LLM Service Examples")
    print("=" * 80)
    print("\nThese examples demonstrate the LLM service functionality.")
    print("Make sure Ollama is running before proceeding.\n")
    
    # Run examples
    await example_health_check()
    await example_list_models()
    await example_basic_generation()
    await example_explanation_modes()
    await example_streaming_generation()
    await example_custom_system_prompt()
    await example_error_handling()
    
    print("\n" + "=" * 80)
    print("Examples Complete")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
