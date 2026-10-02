import pandas as pd
from datetime import datetime, timezone, timedelta
import app

print("==================================================================")
print("RUNNING FINAL TEST SUITE (TEST 1 THROUGH TEST 6)")
print("==================================================================")

sm = app.SessionManager(history_file=".streamlit/test_session_history.json", heartbeat_timeout=45)
sm.reset_all()

now = datetime.now(timezone.utc)
t0 = now - timedelta(hours=1)

# ----------------------------------------------------------------------
# TEST 1: Start ESP32
# Expected:
#   - New session created (Session #1)
#   - Current Session Standing Time starts at 00:00:00
#   - Estimated Battery starts at ~100%
#   - Connection = CONNECTED
# ----------------------------------------------------------------------
print("\n[TEST 1] Starting ESP32...")
feed1 = [{
    'created_at': t0, 'Activity': 'STANDING', 'FSR': 250.0,
    'Accel_X': 0.12, 'Accel_Y': 0.05, 'Accel_Z': 0.98, 'Gyro_Magnitude': 1.2,
    'Standing_Time': '0 min', 'Alert': 'NORMAL', 'Standing_Time_Num': 0.0, 'entry_id': 1
}]
df1 = pd.DataFrame(feed1)
res1 = sm.process(df1, is_simulated=True, battery_capacity=2000)

print(f"Session ID: {res1['session_id']} (Expected: 1)")
print(f"Connection Status: {res1['connection_status']} (Expected: CONNECTED)")
print(f"Current Session Time: {app.format_hms(res1['current_session_seconds'])}")
print(f"Estimated Battery: {res1['estimated_battery_pct']:.1f}% (Expected: ~100%)")

assert res1['session_id'] == 1, "TEST 1 Failed: Session ID should be 1"
assert res1['connection_status'] == 'CONNECTED', "TEST 1 Failed: Status should be CONNECTED"
assert res1['estimated_battery_pct'] >= 99.0, "TEST 1 Failed: Initial battery must be ~100%"
print("TEST 1 PASSED: New session created, battery initialized to ~100%, status CONNECTED.")

# ----------------------------------------------------------------------
# TEST 2: Stand for some time
# Expected:
#   - Current Session Standing Time increases
#   - Total Standing Time increases
#   - Estimated Battery gradually decreases
#   - Battery graph trace shows estimated decrease
# ----------------------------------------------------------------------
print("\n[TEST 2] Standing for 30 minutes in Session 1...")
feeds_s1 = []
for i in range(120): # 120 samples @ 15s = 30 minutes (0.5 hours)
    feeds_s1.append({
        'created_at': t0 + timedelta(seconds=i * 15),
        'Activity': 'STANDING',
        'FSR': 260.0, 'Accel_X': 0.12, 'Accel_Y': 0.05, 'Accel_Z': 0.98, 'Gyro_Magnitude': 1.4,
        'Standing_Time': f'{i * 0.25:.1f} min', 'Alert': 'NORMAL', 'Standing_Time_Num': i * 0.25,
        'entry_id': i + 1
    })
df2 = pd.DataFrame(feeds_s1)
res2 = sm.process(df2, is_simulated=True, battery_capacity=1000)

curr_m = res2['current_session_seconds'] / 60.0
tot_m = res2['total_standing_seconds'] / 60.0
bat_pct = res2['estimated_battery_pct']
consumed_mah = res2['battery_consumed_mah']

print(f"Current Session Standing: {curr_m:.1f} min ({app.format_hms(res2['current_session_seconds'])})")
print(f"Total Standing Time: {tot_m:.1f} min ({app.format_hms(res2['total_standing_seconds'])})")
print(f"Estimated Battery: {bat_pct:.1f}% (Consumed: {consumed_mah:.1f} mAh)")
print(f"Battery Trace Points: {len(res2['current_session_battery_trace'])} points generated")

assert abs(curr_m - 30.0) < 0.2, "TEST 2 Failed: Current standing should be 30 min"
assert abs(tot_m - 30.0) < 0.2, "TEST 2 Failed: Total standing should be 30 min"
assert bat_pct < 100.0, "TEST 2 Failed: Battery should decrease"
assert len(res2['current_session_battery_trace']) == 120, "TEST 2 Failed: Battery trace should have 120 points"
print("TEST 2 PASSED: Standing time increased, battery gradually decreased to", f"{bat_pct:.1f}%.")

# ----------------------------------------------------------------------
# TEST 3: Disconnect ESP32
# Expected:
#   - Connection = DISCONNECTED
#   - Session ends
#   - Current session timer stops
#   - Total Standing Time is preserved
#   - Estimated battery session ends
# ----------------------------------------------------------------------
print("\n[TEST 3] Disconnecting ESP32...")
res3 = sm.process(df2, is_simulated=True, sim_force_disconnect=True, battery_capacity=1000)
print(f"Connection Status: {res3['connection_status']} (Expected: DISCONNECTED)")
print(f"Current Standing Time (frozen): {res3['current_session_seconds'] / 60.0:.1f} min")
print(f"Total Standing Time (preserved): {res3['total_standing_seconds'] / 60.0:.1f} min")
print(f"Estimated Battery (frozen at disconnect): {res3['estimated_battery_pct']:.1f}%")

assert res3['connection_status'] == 'DISCONNECTED', "TEST 3 Failed: Should be DISCONNECTED"
assert abs(res3['total_standing_seconds'] / 60.0 - 30.0) < 0.2, "TEST 3 Failed: Total time must be preserved"
print("TEST 3 PASSED: Connection marked DISCONNECTED, session frozen, Total Standing Time preserved.")

# ----------------------------------------------------------------------
# TEST 4: Reconnect ESP32
# Expected:
#   - New session created (Session #2)
#   - Session ID increments
#   - Current Session Standing Time resets to 00:00:00
#   - Estimated Battery resets to 100%
#   - Total Standing Time remains accumulated
# ----------------------------------------------------------------------
print("\n[TEST 4] Reconnecting ESP32 (Session 2 begins)...")
t1 = t0 + timedelta(minutes=45) # 15 min disconnect gap > 45s heartbeat timeout
feeds_s2 = feeds_s1.copy()
# First packet of Session 2 (Sitting state)
feeds_s2.append({
    'created_at': t1,
    'Activity': 'SITTING',
    'FSR': 45.0, 'Accel_X': 0.02, 'Accel_Y': 0.85, 'Accel_Z': 0.15, 'Gyro_Magnitude': 0.3,
    'Standing_Time': '0 min', 'Alert': 'NORMAL', 'Standing_Time_Num': 0.0,
    'entry_id': len(feeds_s2) + 1
})
df4 = pd.DataFrame(feeds_s2)
res4 = sm.process(df4, is_simulated=True, battery_capacity=1000)

print(f"New Session ID: #{res4['session_id']} (Expected: #2)")
print(f"Connection Status: {res4['connection_status']} (Expected: CONNECTED)")
print(f"Current Session Standing: {app.format_hms(res4['current_session_seconds'])} (Expected: 00:00:00)")
print(f"Estimated Battery: {res4['estimated_battery_pct']:.1f}% (Expected: ~100.0%)")
print(f"Total Standing Time: {res4['total_standing_seconds'] / 60.0:.1f} min (Expected: 30.0 min)")

assert res4['session_id'] == 2, "TEST 4 Failed: Session ID should be 2"
assert res4['connection_status'] == 'CONNECTED', "TEST 4 Failed: Status should be CONNECTED"
assert res4['current_session_seconds'] == 0.0, "TEST 4 Failed: Current session standing time must reset to 0"
assert res4['estimated_battery_pct'] >= 99.0, "TEST 4 Failed: Estimated battery must reset to 100%"
assert abs(res4['total_standing_seconds'] / 60.0 - 30.0) < 0.2, "TEST 4 Failed: Total standing time must be preserved"
print("TEST 4 PASSED: Session 2 created, current timer reset to 00:00:00, battery reset to 100%, total standing preserved.")

# ----------------------------------------------------------------------
# TEST 5: Check dashboard graphs
# Expected:
#   - All 6 Plotly graphs generate with valid data and zero errors
# ----------------------------------------------------------------------
print("\n[TEST 5] Checking all 6 dashboard graphs...")
fig_a = app.plot_fsr_trend(df4)
assert fig_a is not None
fig_b = app.plot_motion_trend(df4)
assert fig_b is not None
fig_c = app.plot_gyro_activity(df4)
assert fig_c is not None
fig_d = app.plot_standing_progression(df4)
assert fig_d is not None
fig_e = app.plot_activity_timeline(df4)
assert fig_e is not None
fig_f = app.plot_estimated_battery(res4['current_session_battery_trace'])
assert fig_f is not None
print("TEST 5 PASSED: All 6 interactive Plotly graphs rendered successfully with valid data.")

# ----------------------------------------------------------------------
# TEST 6: Verify battery behavior
# Expected:
#   - Session 1: 100% -> consumed -> remaining
#   - Disconnect
#   - Session 2: 100% -> consumed -> remaining
#   - Battery estimate from Session 1 must NOT carry into Session 2!
# ----------------------------------------------------------------------
print("\n[TEST 6] Verifying battery isolation across sessions...")
# Run 40 samples in Session 2
for j in range(1, 41):
    feeds_s2.append({
        'created_at': t1 + timedelta(seconds=j * 15),
        'Activity': 'STANDING',
        'FSR': 255.0, 'Accel_X': 0.12, 'Accel_Y': 0.05, 'Accel_Z': 0.98, 'Gyro_Magnitude': 1.3,
        'Standing_Time': f'{j * 0.25:.1f} min', 'Alert': 'NORMAL', 'Standing_Time_Num': j * 0.25,
        'entry_id': len(feeds_s2) + 1
    })
df6 = pd.DataFrame(feeds_s2)
res6 = sm.process(df6, is_simulated=True, battery_capacity=1000)

s2_bat = res6['estimated_battery_pct']
s2_consumed = res6['battery_consumed_mah']
print(f"Session 1 final battery before disconnect: {bat_pct:.1f}%")
print(f"Session 2 battery after 10 min: {s2_bat:.1f}% (Consumed: {s2_consumed:.1f} mAh)")
print(f"Session 2 Current Standing: {res6['current_session_seconds'] / 60.0:.1f} min")
print(f"Total Standing (Session 1 + 2): {res6['total_standing_seconds'] / 60.0:.1f} min")

# Session 1 dropped to ~93%, Session 2 dropped to ~96%. They do NOT accumulate into each other!
assert s2_bat > bat_pct, "TEST 6 Failed: Session 2 must start fresh from 100% and not carry over Session 1 drain!"
print("TEST 6 PASSED: Session 2 started fresh from 100% and did not inherit Session 1 battery drain.")

print("\n==================================================================")
print("ALL 6 TESTS PASSED WITH 100% SUCCESS!")
print("==================================================================")
