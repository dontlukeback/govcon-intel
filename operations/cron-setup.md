# Automated Pipeline Setup

Two options for scheduling the Sunday night pipeline run on macOS. Start with cron (simpler), switch to launchd if you need reliability through sleep/wake cycles.

---

## Option 1: cron (simple)

Works well if your Mac is awake and running at the scheduled time. If it's asleep, the job silently skips.

### Setup

```bash
# Open the crontab editor
crontab -e
```

Add this line:

```
0 21 * * 0 cd /Users/luke/Personal/govcon-intel && ./generate.sh >> output/cron.log 2>&1
```

**What this means:**
- `0 21` -- 9:00 PM
- `* *` -- any month, any day-of-month
- `0` -- Sunday (0 = Sunday in cron)
- The rest: cd into the project, run the pipeline, append all output to `cron.log`

### Verify it's saved

```bash
crontab -l
```

You should see your entry listed.

### Test it manually

```bash
cd /Users/luke/Personal/govcon-intel && ./generate.sh >> output/cron.log 2>&1
```

### Cron gotchas on macOS

1. **PATH is minimal in cron.** If `python3` isn't found, add the full path:
   ```
   0 21 * * 0 cd /Users/luke/Personal/govcon-intel && PATH=/usr/local/bin:/opt/homebrew/bin:$PATH ./generate.sh >> output/cron.log 2>&1
   ```

2. **macOS may prompt for permissions.** Go to System Settings > Privacy & Security > Full Disk Access and add `/usr/sbin/cron` (or Terminal.app).

3. **Sleep = missed jobs.** If your Mac is asleep at 9 PM Sunday, the job does not run and does not retry. Use launchd (Option 2) if this is a problem.

---

## Option 2: launchd (recommended for macOS)

launchd is macOS's native job scheduler. Key advantage: if the Mac is asleep at the scheduled time, it runs the job when the Mac wakes up.

### Step 1: Create the plist file

Save this as `~/Library/LaunchAgents/com.govcon-intel.pipeline.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>

    <key>Label</key>
    <string>com.govcon-intel.pipeline</string>

    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>-c</string>
        <string>cd /Users/luke/Personal/govcon-intel && PATH=/usr/local/bin:/opt/homebrew/bin:/usr/bin:$PATH ./generate.sh >> output/cron.log 2>&1</string>
    </array>

    <key>StartCalendarInterval</key>
    <dict>
        <key>Weekday</key>
        <integer>0</integer>
        <key>Hour</key>
        <integer>21</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>

    <key>StandardOutPath</key>
    <string>/Users/luke/Personal/govcon-intel/output/launchd-stdout.log</string>

    <key>StandardErrorPath</key>
    <string>/Users/luke/Personal/govcon-intel/output/launchd-stderr.log</string>

    <key>EnvironmentVariables</key>
    <dict>
        <key>HOME</key>
        <string>/Users/luke</string>
        <key>LANG</key>
        <string>en_US.UTF-8</string>
    </dict>

</dict>
</plist>
```

### Step 2: Install the plist

```bash
# Copy the file (if you didn't create it directly in LaunchAgents)
cp com.govcon-intel.pipeline.plist ~/Library/LaunchAgents/

# Load it
launchctl load ~/Library/LaunchAgents/com.govcon-intel.pipeline.plist
```

### Step 3: Verify it's loaded

```bash
launchctl list | grep govcon
```

You should see `com.govcon-intel.pipeline` in the output. A `0` in the status column means it last ran successfully. A `-` means it hasn't run yet.

### Step 4: Test it now (without waiting for Sunday)

```bash
# Manually trigger the job
launchctl start com.govcon-intel.pipeline

# Check if it ran
cat /Users/luke/Personal/govcon-intel/output/launchd-stdout.log
cat /Users/luke/Personal/govcon-intel/output/launchd-stderr.log
```

### Managing the launchd job

```bash
# Stop/disable the job
launchctl unload ~/Library/LaunchAgents/com.govcon-intel.pipeline.plist

# Reload after editing the plist
launchctl unload ~/Library/LaunchAgents/com.govcon-intel.pipeline.plist
launchctl load ~/Library/LaunchAgents/com.govcon-intel.pipeline.plist

# Check job status
launchctl list com.govcon-intel.pipeline
```

---

## Adding Notifications

To get a ping when the pipeline finishes (success or failure), add this to the end of `generate.sh` or wrap the cron/launchd command:

### macOS native notification

```bash
# Add to the end of generate.sh:
osascript -e 'display notification "Pipeline complete. Check output/" with title "GovCon Intel"'
```

### ntfy.sh (push notification to your phone)

```bash
# Add to the end of generate.sh:
curl -s -d "GovCon pipeline complete: ${#GENERATED[@]} generated, ${#SKIPPED[@]} skipped" ntfy.sh/govcon-intel-pipeline
```

Subscribe to the topic `govcon-intel-pipeline` in the ntfy app on your phone.

---

## Choosing Between cron and launchd

| Factor | cron | launchd |
|--------|------|---------|
| Setup complexity | 1 line | XML plist file |
| Runs if Mac was asleep | No | Yes (runs on wake) |
| macOS native | Legacy (but works) | Yes |
| Easy to test | Run command manually | `launchctl start` |
| Logging | Append to file yourself | Built-in stdout/stderr paths |
| Survives reboots | Yes | Yes |

**Recommendation:** Start with cron since it's one line and you can always re-run manually Monday morning if it missed. Switch to launchd if you find yourself frequently re-running because the Mac was asleep.
