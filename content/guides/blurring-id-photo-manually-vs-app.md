---
title: "Blurring your ID yourself vs using a dedicated app"
subtitle: "What manual editing gets right, what it misses, and when each approach is enough."
description: "Blurring an ID photo with a markup tool is better than nothing, but it misses things a dedicated redaction app handles by default. Here's the honest comparison."
date: 2026-07-20
lastmod: 2026-07-20
weight: 9
faq:
  - q: "Is blurring my ID photo with my phone's markup tool good enough?"
    a: "It's better than sending an unedited photo, but it has real gaps: blur and pixelation can sometimes be reversed, it's easy to miss a field like the machine-readable zone if you don't know to cover it, and there's no watermark tying the copy to one purpose."
  - q: "Can blurred text actually be recovered?"
    a: "Under the right conditions, yes — light blur and pixelation are lossy but not always destructive, and there's documented research on reconstructing text from both. A solid, opaque block removes the pixels entirely and can't be reversed the same way."
  - q: "What does a dedicated redaction app do differently?"
    a: "It's built around the specific fields a passport or ID actually has — including ones people forget, like the machine-readable zone — applies solid, non-reversible redaction by default, adds a watermark, and flattens the result so there's no editable layer left underneath."
  - q: "When is manual editing genuinely fine?"
    a: "For very low-stakes sharing where you control both ends — say, texting a family member a partial view they've already seen in person. For anything leaving your control, the gaps above start to matter."
---

Your phone already has a markup tool. Draw a black box or a blur over your passport number, and it feels done. Mostly, it is — but there are a few specific ways this falls short of what a copy meant to leave your hands should actually protect.

## What manual editing gets right

Covering the obvious field — usually the document number — with a black box or a heavy scribble stops a casual glance from reading it. For low-stakes situations where you trust exactly who's receiving the image and it's staying with them, that's often genuinely enough.

## Where it falls short

**Blur and pixelation aren't always final.** Light blur and low-strength pixelation are lossy, not destructive — under the right conditions, the original text can sometimes be reconstructed, a documented limitation of both techniques. A **solid, opaque block** removes the pixel data entirely and doesn't have this problem; not every markup tool defaults to one.

**It's easy to miss a field you don't know to look for.** Most people manually redacting a passport remember the number. Far fewer think of the **[machine-readable zone]({{< relref "/guides/what-is-the-mrz-machine-readable-zone.md" >}})** — it re-encodes the number, birth date and more, so missing it undoes the rest of the redaction. Date of birth and signature get missed too, since they don't look as obviously "sensitive" as a document number.

**There's no watermark.** A manually blurred photo is still just a photo — if it's forwarded beyond where it was meant to go, nothing in the image ties it to the specific request it was made for.

**The original often still exists next to it.** Markup tools frequently edit a duplicate, but the source photo — unredacted — commonly stays in the camera roll, and it's easy to grab and send the wrong one under pressure.

## What a dedicated redaction flow does differently

It's built around what's actually on a passport or ID: solid, non-reversible boxes by default (not blur), prompts for the fields people forget, a watermark applied automatically, and a flattened export with no editable layer underneath to peel back later. [Anonymize my ID](/#get) does exactly this, entirely on-device — see [how to redact a passport or ID card]({{< relref "/guides/how-to-redact-a-passport-or-id.md" >}}) for the full method.

## When manual editing is genuinely fine

If you're sending a partial view to someone who has already seen the original in person, and it never leaves that conversation, a quick manual cover is proportionate. The gaps above matter most exactly when a copy is heading somewhere you don't fully control — which, for most of the requests in this guide series, is precisely the situation.
