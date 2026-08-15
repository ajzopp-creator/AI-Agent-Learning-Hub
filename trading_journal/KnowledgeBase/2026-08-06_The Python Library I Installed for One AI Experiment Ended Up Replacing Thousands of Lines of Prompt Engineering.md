---
title: "The Python Library I Installed for One AI Experiment Ended Up Replacing Thousands of Lines of Prompt Engineering"
source: "https://medium.com/@SulemanSafdar/the-python-library-i-installed-for-one-ai-experiment-ended-up-replacing-thousands-of-lines-of-a0f710f6b8e3#id_token=eyJhbGciOiJSUzI1NiIsImtpZCI6ImYxMGY4NzQwNWE5NzljMWRmMzZkZjI2NjA2NzM0ZjMzY2Q4NWMyNzEiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL2FjY291bnRzLmdvb2dsZS5jb20iLCJhenAiOiIyMTYyOTYwMzU4MzQtazFrNnFlMDYwczJ0cDJhMmphbTRsamRjbXMwMHN0dGcuYXBwcy5nb29nbGV1c2VyY29udGVudC5jb20iLCJhdWQiOiIyMTYyOTYwMzU4MzQtazFrNnFlMDYwczJ0cDJhMmphbTRsamRjbXMwMHN0dGcuYXBwcy5nb29nbGV1c2VyY29udGVudC5jb20iLCJzdWIiOiIxMTMwNDMwNjE5NjEyODg0ODc3NDAiLCJlbWFpbCI6ImFqem9wcEBnbWFpbC5jb20iLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwibmJmIjoxNzg2MDQ2Nzg1LCJuYW1lIjoiVG9ueSBab3BwaSIsInBpY3R1cmUiOiJodHRwczovL2xoMy5nb29nbGV1c2VyY29udGVudC5jb20vYS9BQ2c4b2NLWXFVaU13WllYcTZCRGVQaFdMSVNraDA0YVJxaXVLblNyM2xaRnJiVTNHYlJZc3VRPXM5Ni1jIiwiZ2l2ZW5fbmFtZSI6IlRvbnkiLCJmYW1pbHlfbmFtZSI6IlpvcHBpIiwiaWF0IjoxNzg2MDQ3MDg1LCJleHAiOjE3ODYwNTA2ODUsImp0aSI6ImJiZWZlZDE4OTMwMzkzYjJkOTkwNjU4NTkyNTgzMjQzMDgzYWVjNGYifQ.Pufk63WnQ1V1dkz7xtvwUHqqGed4RWfnKC2cjHG-LYIGWk1lq-3bnQUw4Xbhywi2-A0dzfugmNjMODRCxlTK6UonF7m_Rx8SzSMEUkLkrYDVwO70X1hTuSNQLbAOtY_TkBRvW3ycSh9JqYWyy0Zht6-h7ZzrNgcEB4zH7-UeO1u8LN5KlqJBSqLctdZyAS5T16-KtqMj06WUgTea-qo2a0oz4MGDUSL8T8lh_1jUeyzXbZmBuWIr_oz9Gy4Z4zbE7Vm5TzgadYdD-icC6frhFMsqM5Uq7anhhSRbb2x3-fuf1y-tUbK1F-75AI-v7Kr4ei2pMQRlXa5F0ZN724kInA"
author:
  - "[[Suleman Safdar]]"
date: "2026-08-06"
published: 2026-08-06
tags:
  - "kb"
kb_type: "article"
ticker_relevance:
  - "Medium"
sector:
origin:
review_status: reviewed-no-match
review_date: 2026-08-06
disposition: Restates contract-over-prompt practice the Hub already implements (Pydantic schemas at all I/O boundaries, domain/infrastructure/application split, python-project-architecture SKILL). No trading-strategy relevance; no change proposed.
---
## For months, I believed prompt engineering was the secret to building reliable AI applications. Every project started with another giant prompt full of instructions, edge cases, and formatting rules. It worked until it didn’t. One small change could break everything. Then I discovered PydanticAI. I expected another AI wrapper. Instead, I found a framework that made AI behave more like traditional software, and it completely changed how I build production AI systems.

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/0*g0i4nw08SXOUpODE)

Photo by Lautaro Andreani on Unsplash

## 1\. I Thought Better Prompts Meant Better AI I Was Solving the Wrong Problem

If you’ve built enough AI applications, you’ve probably written prompts like this:

> *“You are an expert financial analyst. Always return valid JSON. Never invent information. Follow these formatting rules. Use these field names. Think step by step…”*

The prompt kept growing.

Every new bug meant another paragraph.

Eventually, one client’s prompt exceeded 500 lines.

It became impossible to maintain.

Even worse…

Different models interpreted the same instructions differently.

That’s when I tried **PydanticAI**.

```c
from pydantic import BaseModel
from pydantic_ai import Agent

class ProductReview(BaseModel):
    sentiment: str
    score: float
    summary: str

agent = Agent(
    "openai:gpt-5.5",
    result_type=ProductReview
)

result = agent.run_sync(
    "Review this laptop. It's fast, quiet, and battery life is excellent."
)

print(result.output)
```

## Why this changed everything

Instead of asking the model to *please* return valid JSON…

I defined exactly what valid output looked like.

The framework handled the rest.

## 2\. Stop Engineering Prompts. Start Designing Contracts.

One realization completely changed how I approached AI.

Traditional software has contracts.

Functions expect inputs.

Functions return outputs.

Why shouldn’t AI?

```c
from pydantic import BaseModel

class Invoice(BaseModel):

    customer: str

    amount: float

    paid: bool
```

Now the AI isn’t simply generating text.

It’s generating structured data that your application can trust.

## Why businesses love this

Reliable software integrates easily.

Random text doesn’t.

## 3\. Type Safety Turned AI Into Something I Could Actually Debug

One frustrating bug kept appearing.

The model returned:

```c
{
  "price": "Forty Dollars"
}
```

The backend expected:

```c
price: float
```

Production crashed.

With PydanticAI…

Validation happens automatically.

```c
from pydantic import BaseModel

class Pricing(BaseModel):

    product: str

    price: float
```

## Deep explanation

Instead of discovering bad data later…

You catch it immediately.

That’s how traditional software behaves.

AI should too.

## 4\. Tool Calling Finally Felt Natural

The biggest improvement wasn’t structured output.

It was structured actions.

Instead of telling the AI about your database…

Let it query the database.

```c
from pydantic_ai import Agent

agent = Agent("openai:gpt-5.5")

@agent.tool
def inventory(product: str) -> int:

    stock = {

        "Keyboard": 42,

        "Mouse": 19

    }

    return stock.get(product, 0)
```

Now users can ask:

> *“Do we still have keyboards?”*

The model doesn’t guess.

It calls your function.

## 5\. AI Agents Became Much Easier to Test

Testing prompts used to feel impossible.

Testing structured agents feels familiar.

```c
examples = [

    "Refund request",

    "Shipping delay",

    "Warranty question"

]

for item in examples:

    print(

        f"Testing: {item}"

    )
```

## Practical examples

Verify:

- Output format
- Required fields
- Tool usage
- Error handling
- Edge cases

AI development starts looking like software engineering again.

## 6\. Dependency Injection Isn’t Just for APIs

One feature I didn’t expect to love was dependency injection.

Instead of hiding everything inside prompts…

Inject your services.

```c
from dataclasses import dataclass

@dataclass
class Database:

    connection: str

db = Database(

    connection="postgres"

)
```

## Why this matters

Swapping databases.

Changing APIs.

Replacing models.

Everything becomes easier because components stay loosely coupled.

## 7\. Combine PydanticAI with Modern Python Libraries

One of my favorite AI stacks today looks like this:

- FastAPI
- PydanticAI
- Docling
- PostgreSQL
- Redis
- Qdrant
```c
stack = [

    "FastAPI",

    "PydanticAI",

    "Docling",

    "Redis",

    "Qdrant"

]

for tool in stack:

    print(tool)
```

## Why developers love this

Every library has one responsibility.

The architecture remains simple as projects grow.

## 8\. One Agent Can Power Multiple Products

After several client projects…

I noticed something interesting.

The business logic barely changed.

Only the use case changed.

The same architecture powered:

- AI Contract Review
- Customer Support
- Resume Screening
- Healthcare Documentation
- Sales Assistants
- Internal Knowledge Systems
```c
products = [

    "Support",

    "Legal",

    "Healthcare",

    "Recruitment",

    "Sales"

]

print(products)
```

## Why this scales

You’re reusing reliable AI infrastructure.

Not rewriting prompts.

## 9\. Package Structured AI Into Premium SaaS Products

One internal automation project became something much bigger.

Instead of selling access to a chatbot…

We sold reliable workflows.

Customers uploaded data.

The AI returned validated results.

Everything integrated directly into existing software.

```c
plans = {

    "Starter": 79,

    "Growth": 299,

    "Enterprise": "Custom"

}

print(plans)
```

## Business opportunities

Build products like:

- AI invoice processing
- Compliance checking
- Contract analysis
- HR automation
- Financial reporting

Structured outputs make enterprise adoption much easier.

## 10\. The Biggest Lesson Was Never About PydanticAI

When I first installed PydanticAI, I thought I was learning another AI framework.

Looking back…

I was actually learning how to treat AI like software instead of magic.

Instead of hoping prompts behaved correctly…

I defined schemas.

Instead of trusting generated text…

I validated structured outputs.

Instead of writing increasingly complicated instructions…

I built reusable agents.

Ironically, I now spend far less time writing prompts than I did a year ago.

Most of my effort goes into designing clean data models, reusable tools, and predictable workflows.

That’s exactly where software engineering has always delivered the most value.

```c
def annual_roi(

    employees,

    tasks_per_day,

    minutes_saved,

    hourly_rate

):

    yearly_hours = (

        employees *

        tasks_per_day *

        minutes_saved *

        260

    ) / 60

    return yearly_hours * hourly_rate

roi = annual_roi(

    employees=120,

    tasks_per_day=18,

    minutes_saved=2,

    hourly_rate=65

)

print(

    f"Estimated Annual Savings: ${roi:,.2f}"

)
```

## Packaging and Pricing Ideas

```c
| Product                            | Pricing Model        |         Example Price |
| ---------------------------------- | -------------------- | --------------------: |
| AI Document Processing API         | Monthly Subscription |        $99–$499/month |
| AI Compliance Platform             | Per User             |   $30–$120/user/month |
| Enterprise Structured AI Suite     | Annual License       | $40,000–$250,000/year |
| Custom AI Workflow Automation      | Project + Support    |      $25,000–$150,000 |
| White-Label Enterprise AI Platform | Enterprise Contract  |  $100,000–$1,000,000+ |
```

The biggest surprise wasn’t that PydanticAI reduced the amount of prompt engineering I had to do it was that it shifted my focus back to sound software engineering practices. By treating AI interactions as structured, validated workflows instead of unpredictable conversations, I built applications that were easier to debug, easier to maintain, and far more trustworthy in production. In the end, clients weren’t paying for clever prompts; they were paying for reliable systems that consistently delivered correct results.