---
title: "You cannot redact your ID for a bank — and shouldn't try"
subtitle: "KYC needs the whole document. The useful skill here is telling a real bank request from a fake one."
description: "Redacting your ID will not get you through a bank's identity check — anti-money-laundering rules require the full document. What to do instead."
date: 2026-07-20
lastmod: 2026-08-07
weight: 21
keywords:
  - "banks"
  - "KYC"
  - "anti-money-laundering"
  - "who asks for ID"
  - "when redaction fails"
answer: "No. Opening or keeping a bank account is a regulated identity check, and anti-money-laundering law requires the institution to capture the complete document — Germany's § 8 GwG says so in as many words. A redacted or watermarked copy fails the check, and the only thing you achieve is a repeat request. Send the full document through the bank's own app or portal, and put your effort into the question that actually matters: whether the request came from your bank at all."
takeaways:
  - "**Redaction does not work here.** AML rules require the complete document; a covered field is a rejected check."
  - "**A watermark does not help either** — a KYC system reads fields, and an overlay across them is a failed capture, not a protection."
  - "**The real risk is a fake request.** Genuine KYC runs inside the bank's app or portal, started by you, never from an inbound email or message."
faq:
  - q: "Can I send my bank a redacted copy of my ID?"
    a: "No. Identity verification for a bank account is a regulated check under anti-money-laundering rules and the institution is required to capture the full document. Germany's Geldwäschegesetz § 8 states the duty explicitly. Cover a field and the check fails — you will simply be asked again."
  - q: "Will a watermark stop my bank accepting the copy?"
    a: "It can, and it is not worth the risk. KYC systems read the document's fields and often compare the photo to a live capture; an overlay across the data page is read as an obstruction or a tampering signal. Use the bank's own upload flow and send the document as it is."
  - q: "Then what protects me when a bank asks for ID?"
    a: "Channel discipline, not redaction. A genuine check happens inside the bank's own app or web portal, in a session you started from the application itself. Nothing legitimate requires you to email a passport photo, message it, or send it to an address someone read out to you on a call."
  - q: "Someone from my bank emailed asking for a copy of my ID. What should I do?"
    a: "Treat it as fraud until proven otherwise. Do not reply to the message or use any number or link in it. Call the number printed on your card or on the bank's official site and ask whether a verification step is genuinely pending on your account. If it is, complete it inside the app."
  - q: "Is this the same for PostIdent, VideoIdent or a mortgage broker?"
    a: "PostIdent and VideoIdent are the same regulated check by another name and need the complete document. A broker or intermediary is not the regulated institution and is a different question — ask which entity is running the check and complete it with that entity directly rather than emailing anyone a copy."
---

This site exists to help you redact documents, so here is the honest boundary of that: **for a bank, redaction is the wrong tool, and using it will not work.**

## Why the full document, and no less

Opening or maintaining an account is a regulated identity check — **KYC**, part of [anti-money-laundering regulation](https://eur-lex.europa.eu/eli/dir/2015/849/oj). The obligation sits on the institution, not on you, and in several jurisdictions it is written as a duty to take a *complete* copy. Germany is the clearest: **§ 8 of the Geldwäschegesetz** requires the obliged entity to make a complete copy or complete digital record of the identity document.

A verification system reads the fields — name, date of birth, document number, expiry, often the [machine-readable zone]({{< relref "/guides/what-is-the-mrz-machine-readable-zone.md" >}}) — and frequently matches the photograph against a live capture of your face. Black bars over any of that are not a privacy setting; they are a failed read. So is a watermark laid across the data page, which some capture systems score as evidence of tampering.

There is no clever partial version of this. The check needs the document.

## What to do instead

The thing genuinely worth guarding here is not *which fields* the bank sees. It is **whether the request came from your bank at all** — because impersonating a bank's verification step is one of the most common ways full ID copies are stolen.

1. **Start the flow yourself.** Open the bank's app or type its address by hand. A real pending verification will be waiting for you there.
2. **Never act on an inbound message.** Not the link, not the phone number, not the "case reference". Fraudulent versions of this request are competent, urgent and well-branded.
3. **Call the number on your card** if you are unsure whether something is really pending.
4. **Refuse email and messaging outright.** No regulated institution needs your passport as an email attachment, and no legitimate process breaks if you decline that channel and use the app.
5. **If you have already sent one**, work through [you already sent an unredacted ID copy]({{< relref "/guides/already-sent-an-unredacted-id-copy.md" >}}).

| | The bank's own app or portal | An email, call or message asking for a copy |
| --- | --- | --- |
| **Who started it?** | You, from the application | Them |
| **Send the full document?** | Yes — the check requires it | No — send nothing at all |
| **Does redaction help?** | No, it fails the check | No, the request itself is the problem |
| **What to do** | Complete it in the app | Call the number on your card |

## Where this site's tools do belong

Redaction and watermarking are for the long tail of requests with **no regulator behind them**: a marketplace buyer, a private landlord, a short-term-rental host, a client, a platform's support desk. Those are the situations where the person asking has no legal claim to your document number, and where a covered field costs you nothing. See [when redacting your ID won't work]({{< relref "/guides/when-redacting-your-id-wont-work.md" >}}) for the boundary, and [how to redact a passport or ID card]({{< relref "/guides/how-to-redact-a-passport-or-id.md" >}}) for the method once you are on the right side of it.
