#!/bin/bash
# Spider-Man's Web-Shooter: Mock Email Dispatcher
# Usage: ./web_shooter_email.sh <email> <property_address> <old_status> <new_status>

EMAIL=$1
ADDRESS=$2
OLD_STATUS=$3
NEW_STATUS=$4
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

LOG_FILE="/home/rdogen/agents/IronMan/sent_emails.log"

echo "[$TIMESTAMP] [SENDGRID-MOCK] Dispatching email to: $EMAIL" >> $LOG_FILE
echo "[$TIMESTAMP] [SENDGRID-MOCK] Subject: URGENT: Zoning Compliance Status Changed" >> $LOG_FILE
echo "[$TIMESTAMP] [SENDGRID-MOCK] Body: Property at $ADDRESS changed from $OLD_STATUS to $NEW_STATUS." >> $LOG_FILE
echo "---------------------------------------------------------" >> $LOG_FILE

exit 0
