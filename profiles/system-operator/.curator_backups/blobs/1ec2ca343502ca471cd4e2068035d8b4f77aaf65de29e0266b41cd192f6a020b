# Google Translate Endpoint (b7s.googletranslate)

## Endpoint

`https://translate.googleapis.com/translate_a/single`

## Client Parameter

| Parameter | Behavior |
|---|---|
| `client=gtx` | Original — aggressively rate-limited (HTTP 429) after a few requests |
| `client=dict-chrome-ex` | Works — no rate limiting observed in practice |

## JSON Response Shape

```
[[["translated text","original text",null,null,10]],null,"detected_lang",null,null,null,0.76,[],[["en"],null,[0.76],["en"]]]
```

The C parser in `src/translate.c` extracts:
- `text`: concatenated segment[0] values from the first inner array
- `src`: the third element of the outer array (detected source language)

## Build

```
cd ~/.config/omarchy/plugins/b7s.googletranslate
make clean && make
```

Requires `libcurl` (dev headers for compile, runtime .so for execution).

## C Source

`src/translate.c` — single-file C99 program. No external JSON parser; uses
a hand-written bounded parser for the specific gtx/dict-chrome-ex response
shape.

## Pitfalls

- The `client=gtx` endpoint is virtually unusable from a home IP. Always
  switch to `dict-chrome-ex`.
- The binary is commit-tracked in the repo — rebuild after any source change
  and commit the updated binary.
- The parser is rigid: it expects the exact Google response shape. If Google
  changes the format, translations will silently fail with "unexpected
  translate response".
