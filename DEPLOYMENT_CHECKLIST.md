# 🚀 Deployment Checklist

Use this checklist to deploy your Subsplash Calendar Bridge to production.

## ✅ **Pre-Deployment Setup**

### **Google Cloud Setup**
- [ ] Google Cloud Project created
- [ ] Google Calendar API enabled
- [ ] Service Account created
- [ ] Service Account has Calendar permissions
- [ ] Credentials JSON file downloaded
- [ ] Service Account email shared with your Google Calendars

### **Google Calendar IDs**
- [ ] Prayer Calendar ID copied
- [ ] BAM Calendar ID copied
- [ ] Kids Calendar ID copied
- [ ] College Calendar ID copied
- [ ] ADT Calendar ID copied
- [ ] Missions Calendar ID copied
- [ ] Youth Calendar ID copied
- [ ] Women's Calendar ID copied
- [ ] Men's Calendar ID copied
- [ ] Lifegroup Calendar ID copied
- [ ] Staff Calendar ID copied
- [ ] Elder Calendar ID copied
- [ ] Worship Calendar ID copied
- [ ] Prophetic Team Calendar ID copied
- [ ] Teaching Team Calendar ID copied
- [ ] Churchwide Calendar ID copied
- [ ] HUB Usage Calendar ID copied

## 🔐 **GitHub Repository Setup**

### **Repository Creation**
- [ ] Repository created (public or private)
- [ ] Code pushed to repository
- [ ] GitHub Actions enabled

### **GitHub Secrets**
- [ ] `GOOGLE_CREDENTIALS` - Full content of service account JSON
- [ ] `PRAYER_CALENDAR_ID` - Your prayer calendar ID
- [ ] `BAM_CALENDAR_ID` - Your BAM calendar ID
- [ ] `KIDS_CALENDAR_ID` - Your kids calendar ID
- [ ] `COLLEGE_CALENDAR_ID` - Your college calendar ID
- [ ] `ADT_CALENDAR_ID` - Your ADT calendar ID
- [ ] `MISSIONS_CALENDAR_ID` - Your missions calendar ID
- [ ] `YOUTH_CALENDAR_ID` - Your youth calendar ID
- [ ] `WOMEN_CALENDAR_ID` - Your women's calendar ID
- [ ] `MEN_CALENDAR_ID` - Your men's calendar ID
- [ ] `LIFEGROUP_CALENDAR_ID` - Your lifegroup calendar ID
- [ ] `STAFF_CALENDAR_ID` - Your staff calendar ID
- [ ] `ELDER_CALENDAR_ID` - Your elder calendar ID
- [ ] `WORSHIP_CALENDAR_ID` - Your worship calendar ID
- [ ] `PROPHETIC_CALENDAR_ID` - Your prophetic team calendar ID
- [ ] `TEACHING_CALENDAR_ID` - Your teaching team calendar ID
- [ ] `CHURCHWIDE_CALENDAR_ID` - Your churchwide calendar ID
- [ ] `HUB_CALENDAR_ID` - Your HUB usage calendar ID

## 🧪 **Testing Phase**

### **Local Testing**
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Test scraping works (`python test_targeted_scraper.py`)
- [ ] Month navigation works (`python month_navigator_scraper.py`)
- [ ] Full sync works with credentials (`python sync_script.py`)

### **GitHub Actions Testing**
- [ ] Manual workflow run triggered
- [ ] Workflow completes successfully
- [ ] Events appear in Google Calendar
- [ ] No errors in workflow logs

## 🚀 **Production Deployment**

### **Initial Run**
- [ ] First automated run at 6-hour interval
- [ ] Events syncing correctly
- [ ] No duplicate events created
- [ ] All calendar types working

### **Monitoring Setup**
- [ ] GitHub Actions notifications enabled
- [ ] Calendar sync monitoring in place
- [ ] Error alerting configured

## 📊 **Verification Steps**

### **Event Verification**
- [ ] Prayer events syncing (Tuesday 5:15 PM, Thursday 6:30 AM)
- [ ] BAM events syncing
- [ ] Kids events syncing
- [ ] College events syncing
- [ ] All other ministry events syncing

### **Data Quality**
- [ ] Event titles correct
- [ ] Dates and times accurate
- [ ] URLs preserved
- [ ] No missing events

## 🔧 **Troubleshooting Preparation**

### **Common Issues**
- [ ] Know how to check GitHub Actions logs
- [ ] Understand how to enable debug mode
- [ ] Know how to check sync results
- [ ] Have backup testing procedures

### **Support Resources**
- [ ] README.md reviewed
- [ ] Troubleshooting section understood
- [ ] Support contacts identified

## 🎯 **Success Criteria**

### **Short Term (Week 1)**
- [ ] All calendars syncing automatically
- [ ] Events appearing in Google Calendar
- [ ] No critical errors in logs
- [ ] Team members can see events

### **Medium Term (Month 1)**
- [ ] Recurring events working correctly
- [ ] Future events extending 6+ months
- [ ] All ministry areas covered
- [ ] Team adoption high

### **Long Term (Ongoing)**
- [ ] Calendar becomes single source of truth
- [ ] Reduced manual calendar management
- [ ] Improved team coordination
- [ ] System runs reliably

## 🚨 **Emergency Procedures**

### **If Sync Fails**
1. Check GitHub Actions logs
2. Verify Google Calendar permissions
3. Check service account status
4. Test locally if needed
5. Roll back to previous version if necessary

### **If Events Duplicate**
1. Check sync logic
2. Verify event matching criteria
3. Clean up duplicate events
4. Adjust event identification

---

## 🎉 **You're Ready to Deploy!**

Once you've completed this checklist, your Subsplash Calendar Bridge will be running automatically and keeping your Google Calendars in sync with your Subsplash events!

**Next Steps:**
1. Push your code to GitHub
2. Set up the secrets
3. Run a manual test
4. Monitor the first automated run
5. Celebrate your automated calendar system! 🎊
