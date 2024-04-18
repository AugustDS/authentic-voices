Solve authenticity crisis online: Start by surfacing authentic product reviews.

No affiliation, no SEO crap, no ads.

### TL;DR

`transcriber.py`
- Downloads youtube videos via url
- Chunk audio with time stamps by silent segments
- Transcribes audio segments (currently via whisper)

`summarizer.py`
- Extract reviews from transcriptions via LLM (GPT-4) 
- Via structured output schames see `models.py`

`aggregator.py`
- Group different reviews according to aspects via LLMs (GPT-4)


### In progress

- Store json data (MongoDB)
- Surface authentic reviews (next.js & vercel)
- UI will support slicing across all useful dimensions
- Show actual quotes and link to correct timestamps

### Next steps
- Run pipeline on 20-30 most authentic product review YouTube channels
- Surface all products with sufficient authentic review points


### Vision
- Include authentic user reviews from reddit
- Become #1 trusted source of authentic reviews online
