from transformers import GPT2Tokenizer


async def on_ready_token():
    tokenizer = GPT2Tokenizer.from_pretrained("microsoft/DialoGPT-medium") #Este codigo faz a tokenização das palavras inseridas pelo usuário.
    text = "Teste"
    tokenized_text = tokenizer.tokenize(text)
    print(len(tokenized_text))