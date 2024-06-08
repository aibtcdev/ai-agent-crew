good_example = """
Survey of Americans shows [47% haven't heard of ChatGPT](https://x.com/emollick/status/1795515457228935658)

- 7% use it on a daily basis
- our intersection is even smaller
- shows how early we are!

Concept of an [agent-computer interface](https://x.com/JamesAlcorn94/status/1794897317503631394)

- SWE-agent paper shows agents need LLM-native interfaces
- Agent-computer interface vs human-computer interface
- Existing interfaces (especially GUI) cause problems for agents
- Agents could design their own (smart contracts come to mind!)

CodeAct framework [suggests using Python instead of JSON](https://x.com/_philschmid/status/1795853856628199619)

- LLM generates python code as the action
- LLM executes python code with an interpreter
- Captures output or error message, then refines
- Released a [paper](https://huggingface.co/papers/2402.01030) and [related dataset](https://huggingface.co/datasets/xingyaoww/code-act) for training

Great O'Reilly write-up on [building with LLMs](https://www.oreilly.com/radar/what-we-learned-from-a-year-of-building-with-llms-part-i/)

- hard to develop products beyond demos
- advice on prompting techniques, structured inputs
- RAG is preferable to fine-tuning
- multi-step workflows perform better
- evaluation is critical, LLM-as-Judge can help assess
- tackle hallucination through prompting and guardrails

Running LLMs continues to get easier

- Llama.cpp [available through Brew](https://x.com/victormustar/status/1795778241744998614)
- AutoAWQ now [using Flash Attention 2](https://x.com/rohanpaul_ai/status/1795196332166070289)
    - can run Mixtral 8x7B MoE with 24gb GPU VRAM
- Jan [surpassed 1M downloads!](https://x.com/janframework/status/1795328213478215999)
    - local, offline, ChatGPT-like interface and more
    - can host local models with OpenAI API

SambaNova designed [a chip that outperforms GPUs](https://x.com/IntuitMachine/status/1795570166706720909)

- the RDU architecture solves current limitations
- performance similar to Groq, impressive output
- this sector will undoubtedly continue to grow

ChatGPT [system prompts leaked!](https://x.com/myfear/status/1795549367580950814)

- modular in design, adapted based on available functionality
- extracted through a custom prompt (common technique)

New paper: [Detecting text from an LLM](https://x.com/jihoontack/status/1795350959482400890)

- ReMoDetect uses reward models to detect aligned LLM-generated texts
- uses human preference for AI-generated text to create reward model
- continually fine-tunes the reward model to further increase predicted rewards

Lots of new models across a lot of categories

- Mistral [released Codestral 22B](https://x.com/dchaplot/status/1795823340533469560) (super powerful, restrictive licensing)
- LLM360 [released K2-65B](https://x.com/llm360/status/1795833911580438807) (fully-open LLM)
- OpenDriveLab [released Vista 2.5B](https://x.com/kashyap7x/status/1795354164874408363) (driving world model)
- Cartesia [released Sonic](https://x.com/cartesia_ai/status/1795856778456084596) (generative voice model and API)
- 2noise [released ChatTTS](https://x.com/Xianbao_QIAN/status/1795490474461118804) (voice generation model)
- Qwen [download stats](https://x.com/huybery/status/1795432194460340708) and Qwen2 coming soon!

Crazy [reverse turing test](https://x.com/AISafetyMemes/status/1795309403824165184)

- LLMs playing "who's the human" using Claude, GPT4, and Gemini
- eerie but fascinating, video games will never be the same!
"""

bad_example = """
- [Whether you're preparing for a hackathon or building an app, you'll eventually need on-chain data.
    
    RSVP in the link below]([https://x.com/hirosystems/status/1796579639982440751](https://x.com/hirosystems/status/1796579639982440751))
    
    - Hosting a workshop next Tues to show an easy way to build lightweight databases of on-chain events for Stacks

- [LangChain is an open source project called GPT Computer Assistant that aims to replicate the ChatGPT desktop app. The project can be found on GitHub at https://github.com/onuratakan/gpt-computer-assistant.](https://x.com/LangChainAI/status/1796942281821585864)
    
    - Easily installed via pip
    - Allows users to send text and screenshots to receive a voice response
    - Praises the speed of the OSS community
- [Mesop, open-source Python UI framework used at Google to build AI/ML apps - Open sourced by Google](https://x.com/rohanpaul_ai/status/1798457077037469962)
    
    - Mesop is an open-source Python UI framework
    - Used at Google to build AI/ML apps
    - Google has open sourced Mesop
- [Steve (Builder.io) would love your feedback https://github.com/BuilderIO/micro-agent…its customizable to your specific test criteria (vitest, jest, lint, tsc, etc)](https://x.com/Steve8708/status/1798720674875560220)
    
    - More useful than just asking chatgpt for code and having to discover where it's broken
    - Customizable to specific test criteria like vitest, jest, lint, tsc
"""
