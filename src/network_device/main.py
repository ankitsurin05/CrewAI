#!/usr/bin/env python
import sys
import warnings
import threading
import time
import requests
import json

from datetime import datetime

import panel as pn
pn.extension(design="material")

from network_device.crew import NetworkDevice,chat_interface

from crewai.agents.agent_builder.base_agent_executor_mixin import CrewAgentExecutorMixin

user_input = None
crew_started = False
flag = False
final_output = ""
updates = ""

API_URL_TEAMS = "https://peg-automation.azure-api.net/open-teams-chats/invoke"

def custom_ask_human_input(self, final_answer: dict) -> str:
    global flag
    global final_output

    if (flag == False):
        final_answer = str(final_answer).replace("`","")
        final_answer = str(final_answer).replace("json","")
        final_answer = str(final_answer).replace("IND-ND4-DEV-CORE-SW-01 ","")
        
        with open("formatting_task.txt", "r") as file:
            insights = file.read()
    

        #insights = json.dumps({"Device_Type": "Switch","Device_Name":"IND-ND4-DEV-CORE-SW-01","Interface_Name":"GigabitEthernet1/3","Problem_Statement":"Interface GigabitEthernet1/3 connected to switch IND-ND4-DEV-CORE-SW-01 has gone down and reporting the value 2.0, placing the interface into critical state."})

        data = json.loads(str(final_answer))
        formatted_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        status_msg = chat_interface.send(f"""<b style="color: blue;">L1-AI agent</b><b>: 📌 <b>Extracting insights...</b> - {formatted_time}\n{insights}\n""", user="Assistant", respond=False)
        time.sleep(3)
        updates = status_msg.object
        
        formatted_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        status_msg.object = updates + f"""\n\n<b style="color: blue;">L1-AI agent</b><b>: 🔍 <b>Generating dynamic relevant commands...</b> - {formatted_time}\n```json{final_answer}```"""  # Update status
        time.sleep(3)
        updates = status_msg.object

        Incident_No = create_incident()
        json_incident_no = json.dumps({"Ticket_Number": Incident_No})

        formatted_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        status_msg.object = updates + f"""\n\n<b style="color: blue;">L1-AI agent</b><b>: 🚨 <b>Creating Incident...</b> - {formatted_time}\n```json\n{json_incident_no}\n```"""  # Update status
        updates = status_msg.object

        print(Incident_No)
        for command in data:
            output = network_api(command)
            final_output += output + "\n\n"
        print(final_output)
        
        final = {"Output": final_output}
        json_final = json.dumps(final)

        formatted_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        status_msg.object = updates + f"""\n\n<b style="color: blue;">L1-AI agent</b><b>: 📡 <b>Pushing command to device...</b> - {formatted_time}"""
        time.sleep(3)
        updates = status_msg.object

        formatted_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        status_msg.object = updates + f"""\n\n<b style="color: blue;">L1-AI agent</b><b>: 📜 <b>Command output captured...</b> - {formatted_time}\n```json\n{json_final}\n```"""  # Additional status
        time.sleep(3)
        updates = status_msg.object

        formatted_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        status_msg.object = updates + f"""\n\n<b style="color: blue;">L1-AI agent</b><b>: 📌 <b>Pasting output in incident...</b> - {formatted_time}"""  # Additional status
        time.sleep(3)
        updates = status_msg.object

        #output2 = network_api2()
        #final_output = output + "\n\n" + output2
        update_ticket(final_output,Incident_No)
        
        response = updates + f"""\n\n<b>Engaging incident-AI agent</b>\n\n<b>An incident has been raised. Incident number</b> - {Incident_No}\n\n<b>A team chat will 🔜 be created 💬</b>\n\n<b style="color: green;">Incident-AI agent</b><b>: Reviewing the incident..</b>\n\n<b style="color: green;">Incident-AI agent</b><b>: Engaging the relevant L2-AI agent...</b>\n\n<b style="color: #FFBF00;">L2-AI agent</b><b>: Analysing the incident and command outputs..</b>\n\n<b style="color: #FFBF00;">L2-AI agent</b><b>: Determines hardware issue .. need physical inspection</b>\n\n<b style="color: #FFBF00;">L2-AI agent</b><b>: Mobilizing onsite engineer for physical inspection of port/cable</b>\n\n"""
        
        #status_msg = chat_interface.send("📌 Extracting insights...", user="Assistant", respond=False)  # Initial status
        #time.sleep(5)  # Simulate processing step 1
    
        #status_msg.object = "🔍 Getting relevant commands..."  # Update status
        #time.sleep(5)  # Simulate processing step 2
        
        status_msg.object = response

        ChatMembers = "703364480@genpact.com;703364474@genpact.com;703342092@genpact.com;703259517@genpact.com"

        create_teams_chat(ChatMembers,Incident_No,"TBD","703364480")

        flag = True

        #chat_interface.send(response, user="Assistant", respond=False)

        prompt = "Please provide feedback on the Final Result and the Agent's actions: "
        chat_interface.send(prompt, user="Assistant", respond=False)

        while user_input == None:
            time.sleep(1)  

        human_comments = user_input
        user_input = None
        
        return human_comments

CrewAgentExecutorMixin._ask_human_input = custom_ask_human_input

def create_incident():
    global flag

    url = "https://peg-automation.azure-api.net/create-incident/invoke"

    payload = json.dumps({
    "u_incident_type": "Infrastructure Restoration",
    "impact": "3",
    "priority": "2",
    "short_description": "Room (IND_JPR_JLN_2F_VC2) is offline",
    "u_reported_on_behalf_of": "a1cb46ef1ba83010cbcea8afe54bcb69",
    "u_category_tier_3": "NA",
    "caller_id": "a1cb46ef1ba83010cbcea8afe54bcb69",
    "subcategory": "teams_room",
    "assignment_group": "Corp.Tech.TIS.Global.TOC.Support.L2",
    "description": "Description-\nIncident ID: DOQWL1-U9D0PJ\nIncident state: New\nIncident created on: March 3, 2025 1:40 UTC\nIncident type: Configured Conferencing Microphone\nTenant: Genpact\nDevice names: IND_JPR_JLN_2F_VC2\nDevice host names: MTRW-S4ARYZ007581H4J\nDevice accounts: MTRoW_IND_JPR_JLN_2F_VC2\n ",
    "contact_type": "email",
    "urgency": "2",
    "company": "6d9fd19e1b60f010cbcea8afe54bcb49",
    "severity": "3",
    "category": "issue",
    "table": "incident"
    })
    headers = {
    'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    flag = True

    json_response = response.json()
    return(json_response["result"].get("number"))

def network_api2():
    url = "https://genpact-dev-iap01.iap-prod.itential.io/operations-manager/triggers/endpoint/TESTING_AENTIC_API/"

    payload = json.dumps({
    "Device_Name": "IND-ND4-DEV-CORE-SW-01",
    "Command": "sh running-config interface Gi1/4"
    })
    headers = {
    'Cookie': 'token=NjQ4OTlhMjQ0Mzk5MGFhNDZjZmFjYzcwNDE0MmM4Nzk=; AWSALB=nTvZgnEMvl854+0RpCgyLGkYLzEv/2Af3YOmS3QgpUc0d4qn6/lt+RSDgBfad3mewszA1WWBgeegefpHaYVn6L31uZ/HF1ue5uEWuHUuQ/TT9a/LPagw7k4Rqdr2; AWSALBCORS=nTvZgnEMvl854+0RpCgyLGkYLzEv/2Af3YOmS3QgpUc0d4qn6/lt+RSDgBfad3mewszA1WWBgeegefpHaYVn6L31uZ/HF1ue5uEWuHUuQ/TT9a/LPagw7k4Rqdr2; connect.sid=s%3ApEFbvya9L1fN4rfoqox78IPtbsDGvzRY.oMa2EWBUgA50OtsBcIkNDspQeUPyVn7GHtyIRjCfJuI',
    'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload, verify=False)

    data = response.json()
    json_response = data["data"]
    ID = json_response.get("_id")

    time.sleep(10)

    url = f"https://genpact-dev-iap01.iap-prod.itential.io/operations-manager/jobs/{ID}"

    payload = {}
    headers = {
    'Cookie': 'token=NjQ4OTlhMjQ0Mzk5MGFhNDZjZmFjYzcwNDE0MmM4Nzk=; AWSALB=THxSrb/my0zrE/PsJZ8Q0KNOj0NaBKFycYg0prB1Q9g51u+Wi/dvkt9QOoqYte62cQPbp9FXH1nk/BEJgrJYPCJJVK3sJO+PZnTUa2ArZ5tz5b6JhzN2m1/SHTze; AWSALBCORS=THxSrb/my0zrE/PsJZ8Q0KNOj0NaBKFycYg0prB1Q9g51u+Wi/dvkt9QOoqYte62cQPbp9FXH1nk/BEJgrJYPCJJVK3sJO+PZnTUa2ArZ5tz5b6JhzN2m1/SHTze; connect.sid=s%3ApEFbvya9L1fN4rfoqox78IPtbsDGvzRY.oMa2EWBUgA50OtsBcIkNDspQeUPyVn7GHtyIRjCfJuI'
    }

    response = requests.request("GET", url, headers=headers, data=payload, verify=False)

    data = response.json()
    json_response = data["data"]
    variables = json_response.get("variables")
    result = variables.get("result")
    final_data = result.get("response")
    #print(final_data)
    if response.status_code == 200:
        return final_data
    else:
        return {
            'status': response.status_code,
            'message': response.text
        }

def network_api(command):
    url = "https://genpact-dev-iap01.iap-prod.itential.io/operations-manager/triggers/endpoint/TESTING_AENTIC_API/"

    payload = json.dumps({
    "Device_Name": "IND-ND4-DEV-CORE-SW-01",
    "Command": command
    })
    headers = {
    'Cookie': 'token=NjQ4OTlhMjQ0Mzk5MGFhNDZjZmFjYzcwNDE0MmM4Nzk=; AWSALB=nTvZgnEMvl854+0RpCgyLGkYLzEv/2Af3YOmS3QgpUc0d4qn6/lt+RSDgBfad3mewszA1WWBgeegefpHaYVn6L31uZ/HF1ue5uEWuHUuQ/TT9a/LPagw7k4Rqdr2; AWSALBCORS=nTvZgnEMvl854+0RpCgyLGkYLzEv/2Af3YOmS3QgpUc0d4qn6/lt+RSDgBfad3mewszA1WWBgeegefpHaYVn6L31uZ/HF1ue5uEWuHUuQ/TT9a/LPagw7k4Rqdr2; connect.sid=s%3ApEFbvya9L1fN4rfoqox78IPtbsDGvzRY.oMa2EWBUgA50OtsBcIkNDspQeUPyVn7GHtyIRjCfJuI',
    'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload, verify=False)

    data = response.json()
    json_response = data["data"]
    ID = json_response.get("_id")

    time.sleep(10)

    url = f"https://genpact-dev-iap01.iap-prod.itential.io/operations-manager/jobs/{ID}"

    payload = {}
    headers = {
    'Cookie': 'token=NjQ4OTlhMjQ0Mzk5MGFhNDZjZmFjYzcwNDE0MmM4Nzk=; AWSALB=THxSrb/my0zrE/PsJZ8Q0KNOj0NaBKFycYg0prB1Q9g51u+Wi/dvkt9QOoqYte62cQPbp9FXH1nk/BEJgrJYPCJJVK3sJO+PZnTUa2ArZ5tz5b6JhzN2m1/SHTze; AWSALBCORS=THxSrb/my0zrE/PsJZ8Q0KNOj0NaBKFycYg0prB1Q9g51u+Wi/dvkt9QOoqYte62cQPbp9FXH1nk/BEJgrJYPCJJVK3sJO+PZnTUa2ArZ5tz5b6JhzN2m1/SHTze; connect.sid=s%3ApEFbvya9L1fN4rfoqox78IPtbsDGvzRY.oMa2EWBUgA50OtsBcIkNDspQeUPyVn7GHtyIRjCfJuI'
    }

    response = requests.request("GET", url, headers=headers, data=payload, verify=False)

    data = response.json()
    json_response = data["data"]
    variables = json_response.get("variables")
    result = variables.get("result")
    final_data = result.get("response")
    #print(final_data)
    if response.status_code == 200:
        return final_data
    else:
        return {
            'status': response.status_code,
            'message': response.text
        }

def update_ticket(output,Ticket_No):
    
    if Ticket_No != "":
    
        url = f"https://prod-20.centralindia.logic.azure.com:443/workflows/8210f4d746c84778a7082b2f3e2e7cfa/triggers/manual/paths/invoke?api-version=2016-10-01&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sysparm_display_value=true&sig=RhpXEjqQnlSdtyoP0e-ErSpeSeyxezcKZroFqhDuTCs&table=incident&query=number={Ticket_No}"

        payload = {}
        headers = {}

        response = requests.request("GET", url, headers=headers, data=payload)
        response_json = response.json()
        result = response_json.get("result",[])
        sys_id = result[0].get("sys_id")

        #print(sys_id)

        url = f"https://prod-25.centralindia.logic.azure.com:443/workflows/8b216c161a0c4425be771f783e2bfdbc/triggers/manual/paths/invoke?api-version=2016-10-01&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=1DiDiN7RSd-mQOGF-8XodmXoZLK46TatKL_iFX1kyj8&table=incident&sys_id={sys_id}"

        payload = json.dumps({
            "work_notes": output
        })
        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)

def create_teams_chat(email_ids,title, file_content, OHR):
    """Formats emails and sends a POST request to an external API."""
    print(title)
    email_string = email_ids#";".join(email_ids)  # Convert list to semicolon-separated string
    now = datetime.now()
    current_time = now.strftime("%Y-%m-%d %H:%M:%S")
    payload = {
        "Emails": email_string,
        "Title": title,
        "Message": f"<br>🔔 <b>Important Update:</b> This incident is being triaged by the AI Agent. The call is actively monitored, and the following AI Agents has taken the following actions to accelerate resolution:<br><br><b>AI Agents:</b><br>1️⃣ L1-AI Agent<br>2️⃣ Incident-AI agent<br>3️⃣ L2-AI agent<br><br><b>Issue Summary:</b><br>📌 Caller Reported Issue: {current_time} UTC - Interface GigabitEthernet1/3 connected to switch IND-ND4-DEV-CORE-SW-01 has gone down and reporting the value 2.0, placing the interface into critical state.<br><br><b>Verification Results:</b> {current_time} UTC <br>✅ The API was executed with a test OHR.<br>✅ Network device disruption.<br><br><b>Recommended Action Plan:</b><br>🔹 Investigate API Response Delays – Engage with the PEG (Platform Engineering Group) and ServiceNow teams to diagnose and resolve API latency issues.<br>🔹 Optimize API Performance – Assess whether infrastructure scaling, caching, or optimization can improve response time.<br>🔹 Implement a Temporary Workaround – If needed.<br><br><b>Key Stakeholders:</b><br>{file_content} <br><br>🔄 <b>Next Steps:</b> The AI Agent will continue monitoring the resolution progress and provide updates as new insights emerge.<br><br>🚀 <b>Target Resolution Goal:</b> Minimize downtime and prevent further disruptions.<br><br><b>✅ Command Output</b><br><br>{final_output}"
    }
 
    headers = {"Content-Type": "application/json"}
 
    try:
        response = requests.post(API_URL_TEAMS, data=json.dumps(payload), headers=headers)
        response.raise_for_status()  # Raise an error for non-2xx responses
        return response.json()  # Return API response as JSON
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

def initiate_chat(message):
    global crew_started
    crew_started = True
    
    try:
        # Initialize crew with inputs
        inputs = {"issue": message + "Need show interface command and running configuration detail only for the interface."}
        #inputs = {"issue": message + "Need to display interface detail with running configuration"}
        crew = NetworkDevice().crew()
        result = crew.kickoff(inputs=inputs)
        
        # Send results back to chat
    except Exception as e:
        chat_interface.send(f"An error occurred: {e}", user="Assistant", respond=False)
    #crew_started = False

def callback(contents: str, user: str, instance: pn.chat.ChatInterface):
    global crew_started
    global user_input
    global flag

    flag = False

    #extract_ticket_number(contents)

    if not crew_started:
        thread = threading.Thread(target=initiate_chat, args=(contents,))
        thread.start()

    else:
        user_input = contents
        thread = threading.Thread(target=initiate_chat, args=(contents,))
        thread.start()

chat_interface.callback = callback 

# Send welcome message
chat_interface.send(
    "Welcome! I'm your Agentic AI Agent",
    user="Assistant",
    respond=False
)

# Make it servable
chat_interface.servable()

