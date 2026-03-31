# 🔧 API Management Guide

## Overview
Admin can now dynamically change API URLs for any feature without editing code or redeploying the bot.

## Admin Commands

### 1. List All Features
```
/listapis
```
Shows all available features that have configurable APIs.

**Features:**
- num (Phone number lookup)
- vehicle (Vehicle registration)
- pincode (Pincode info)
- ifsc (Bank IFSC code)
- ip (IP geolocation)
- gmail (Gmail info)
- imei (IMEI lookup)
- bomber (SMS bomber)

### 2. View Current API URL
```
/getapi <feature>
```

**Examples:**
- `/getapi num` - View current phone number API
- `/getapi vehicle` - View current vehicle API
- `/getapi` - View ALL API URLs

### 3. Change API URL
```
/setapi <feature> <new_url>
```

**Examples:**
```
/setapi num https://newapi.com/api/num?number=

/setapi vehicle https://api2.com/vehicle?rc=

/setapi bomber https://bomber-api.com/bomb?phone=
```

**Important Notes:**
- URL should include the parameter placeholder at the end
- For example: `https://api.com/num?number=` (bot will append the actual number)
- Changes take effect immediately
- No restart required

## Current Default APIs

```
num: https://osint-num-info.gauravcyber0.workers.dev/?mobile=
vehicle: https://prosnal-vehicle.gauravcyber0.workers.dev/?vehicle=
pincode: https://pin-code-info.gauravcyber0.workers.dev/?pincode=
ifsc: https://ifsc-code-info.gauravcyber0.workers.dev/?ifsc=
ip: http://ip-api.com/json/
gmail: https://gmail-info-api-two.vercel.app/info?mail=
imei: https://imei-number-infoo.vercel.app/api/imei?imei=
bomber: https://bomm.gauravcyber0.workers.dev/?phone=
```

## Use Cases

1. **API Provider Changed:** Quickly switch to new provider
2. **API Down:** Switch to backup API
3. **Better API Found:** Upgrade without code changes
4. **Testing:** Test new APIs before making permanent

## Security

- Only admin (Piyushhu) can use these commands
- Changes are stored in memory (reset on bot restart)
- For permanent changes, update the `API_URLS` dictionary in code

## Example Workflow

1. Check current API:
   ```
   /getapi num
   ```

2. Change to new API:
   ```
   /setapi num https://newapi.com/phone?mobile=
   ```

3. Test the command:
   ```
   /num 9999999999
   ```

4. If working, keep it. If not, revert:
   ```
   /setapi num https://osintapi.in/api/num?number=
   ```

---

**Created by:** P1yu5h{6_9} 💀
