# Gapline Demo Walkthrough

1. Start the server with `python manage.py runserver`.
2. Open `http://127.0.0.1:8000/accounts/login/`.
3. Login as `demo` with password `gapline-demo`.
4. Open the seeded watchlist.
5. Mark the seeded stocks understood to create explicit baselines.
6. Open Demo Controls.
7. Advance replay one day.
8. Return to the dashboard.
9. Show dynamic counts for Needs Attention, Verify Data, Routine, and No Baseline.
10. Explain TCS as Routine because it moved with NIFTYIT.
11. Explain INFY as Needs Attention because its residual diverged from NIFTYIT.
12. Open the INFY Change Receipt.
13. Show the 45/55 arithmetic: own surprise plus benchmark divergence equals the attention score.
14. Advance enough replay days to show TATAMOTORS reversal.
15. Show HDFCBANK as Verify Data because the latest observation is delayed.
16. Show RELIANCE as Verify Data because DemoReplayProvider and DemoConflictProvider disagree.
17. Use the dashboard cards to mark INFY understood again.
18. Refresh the browser.
19. Confirm the checkpoint persists and page views did not create new checkpoints.
20. Optionally inject an out-of-order quote through `market.services.record_observation`.
21. Confirm the newer `as_of` value remains current.
22. Reset with `python manage.py reset_demo`.

Second account: `second` / `gapline-second`.
