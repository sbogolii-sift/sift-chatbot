from transformers import GPT2Tokenizer, TextDataset, DataCollatorForLanguageModeling, \
    GPT2LMHeadModel, TrainingArguments, Trainer

tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
data = TextDataset(
    tokenizer=tokenizer,
    file_path='api-reference.txt',
    block_size=32
)

data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)

model = GPT2LMHeadModel.from_pretrained('gpt2')

training_args = TrainingArguments(
    output_dir='./gpt2_sift_api',
    overwrite_output_dir=True,
    num_train_epochs=10,
    per_device_train_batch_size=32,
    per_device_eval_batch_size=32,
    warmup_steps=len(data.examples),
    logging_steps=50,
    load_best_model_at_end=True,
    evaluation_strategy='epoch',
    save_strategy='epoch'
)

trainer = Trainer(
    model=model,
    args=training_args,
    data_collator=data_collator,
    train_dataset=data.examples[:int(len(data.examples) * 0.8)],
    eval_dataset=data.examples[int(len(data.examples) * 0.8):]
)

trainer.train()

trainer.evaluate()

trainer.save_model()
