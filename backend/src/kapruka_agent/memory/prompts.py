"""
Prompts for the memory steps.

These are the code versions. With Langfuse on, a prompt of the same name
(observability.PROMPT_NAMES) overrides them without a redeploy.
Variables use Langfuse's {{double_braces}}.
"""

MEMORY_EXTRACT = """\
You maintain long-term memory for Rukmani, a gift-shopping assistant at Kapruka (Sri Lanka).
Read the latest exchange and list facts that will help her serve this customer NEXT time.

KEEP facts like:
- people they buy for, with relationship and useful details
  ("Customer's wife is 25 and loves chocolate", "Customer's mother Kamala lives in Kandy")
- recurring occasions and dates ("Wife's birthday is on 12 March")
- preferences and dislikes ("Prefers flowers over cakes", "Usual budget is around LKR 10,000")
- the customer's name and preferred language, if given
- anything they explicitly ask you to remember (set explicit = true)

NEVER keep:
- phone numbers, email addresses, street addresses, payment or order details
- one-off details of this order (quantities, icing text, delivery date of this order)
- anything about Rukmani or the shop itself

Write each fact as one short sentence in ENGLISH, even if the chat is in Sinhala or Tamil.
Do not repeat facts already known. If there is nothing new worth keeping, return no facts.

Already known:
{{known_facts}}

Latest exchange:
{{conversation}}
"""

CONVERSATION_SUMMARY = """\
Summarise this shopping conversation between a customer and Rukmani (Kapruka's gift
assistant) so she can continue it without the full history.

Keep: who the gift is for, the occasion, budget, city, delivery date, products shown or
chosen (with ids and prices), cart changes, checkout details agreed, and open questions.
Drop small talk. Max 150 words, in English.

Summary so far:
{{previous_summary}}

Newer messages to fold in:
{{conversation}}
"""
