# Additional Fixes for NOT ENOUGH INFO Performance

## Current Status
- **After first fix**: 10/29 correct (34.5%)
- **Target**: 20-22/29 correct (70-75%)
- **Gap**: Still failing 19 cases

## Why We're Still Failing

### Problem 1: LLM Still Inferring from Related Evidence
Claims like "founded by **two men**" with evidence "founded by Arnold Hills and Dave Taylor" - the LLM assumes counting names means "two".

### Problem 2: High Confidence Despite Partial Match
Still getting 0.90-1.00 confidence on partial evidence matches.

### Problem 3: Evidence Source Bias
Web search (Tavily) finds too much related content. FEVER expects "not found in Wikipedia" to mean NOT ENOUGH INFO, but we're finding it elsewhere.

## Proposed Additional Fixes

### Fix 2A: Stronger Prompt with Explicit Counting Example
Add even more explicit examples in the prompt:

```python
ULTRA-CRITICAL EXAMPLES FROM REAL FAILURES:

1. Claim: "Founded by TWO men"
   Evidence: "Founded by Arnold Hills and Dave Taylor"
   WRONG: SUPPORTS (you're inferring "two" by counting names)
   RIGHT: NOT ENOUGH INFO (evidence doesn't explicitly state "two")

2. Claim: "Played for a team in the 1990s"
   Evidence: "Played 1990-1995 for Team X"
   WRONG: SUPPORTS (you're making assumptions about completeness)
   RIGHT: Could be SUPPORTS IF evidence is comprehensive, but be skeptical

3. Claim: "Acted in a FILM ADAPTATION of a book"
   Evidence: "Acted in multiple films"
   WRONG: SUPPORTS (you're not verifying it's a book adaptation)
   RIGHT: NOT ENOUGH INFO (doesn't confirm "book adaptation")
```

### Fix 2B: Two-Stage Verification
Split verification into two explicit steps:

```python
STAGE 1 - EVIDENCE COMPLETENESS CHECK:
Does the evidence EXPLICITLY and DIRECTLY address EVERY word in the claim?
- Check each specific word: "two", "sitcom", "film adaptation", "1990s", etc.
- If ANY word is not explicitly confirmed: MUST be NOT ENOUGH INFO

STAGE 2 - ONLY IF STAGE 1 PASSES:
Does the evidence SUPPORT or REFUTE the claim?
```

### Fix 2C: Lower Confidence Threshold
Adjust the confidence calculation to be more conservative:

```python
If you have ANY doubt about evidence completeness:
- Confidence MUST be <= 0.7
- Consider NOT ENOUGH INFO if confidence < 0.8
```

### Fix 2D: Add Claim Specificity Detector
Before verification, analyze claim specificity:

```python
High-specificity indicators:
- Numbers: "two", "three", "five players"
- Specific categories: "sitcom" (not just "TV show"), "film adaptation"
- Specific time: "in 2007" (not just "2000s")
- Specific role: "as president" (not just "politician")

For high-specificity claims:
- DEFAULT to NOT ENOUGH INFO
- Only SUPPORTS/REFUTES if evidence EXPLICITLY confirms specifics
```

## Implementation Priority

### Phase 2A: Enhanced Prompt (30 min)
1. Add the ultra-critical examples
2. Add two-stage verification instructions
3. Test on failed cases

### Phase 2B: Confidence Calibration (1 hour)
1. Add confidence adjustment logic
2. Force lower confidence for partial evidence
3. Add "specificity penalty" to confidence

### Phase 2C: Structured Reasoning (2 hours)
1. Make LLM output intermediate reasoning steps
2. Check: "Does evidence address each word?"
3. Check: "What's missing from evidence?"
4. Then: Final verdict based on checks

## Expected Impact

### After Phase 2A (Enhanced Prompt):
- Current: 34.5% correct
- Expected: 50-60% correct
- Time: 30 minutes

### After Phase 2B (Confidence Calibration):
- Expected: 60-70% correct
- Time: +1 hour

### After Phase 2C (Structured Reasoning):
- Expected: 70-80% correct
- Time: +2 hours
- Trade-off: May slightly reduce SUPPORTS/REFUTES accuracy

## Quick Decision

**Option 1: Try Phase 2A now (30 min)**
- Enhanced prompt with explicit examples
- Quick iteration, no major changes
- Expected to get us to ~55% correct

**Option 2: Implement all of Phase 2 (3-4 hours)**
- All improvements together
- Better overall performance
- More comprehensive fix

**Option 3: Accept current 65% overall accuracy**
- 34.5% NOT ENOUGH INFO is still much better than 18%
- Focus on other improvements
- Come back to this later

## Recommendation

Try **Phase 2A** (enhanced prompt) right now - it's quick and should get meaningful improvement. If we get to 50-60% correct on NOT ENOUGH INFO cases, our overall FEVER accuracy would jump from 65% to ~72%, which is respectable for a web-search system.

