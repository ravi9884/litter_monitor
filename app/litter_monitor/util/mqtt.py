import paho.mqtt.client as mqtt

def disable_warning(broker: str = "192.168.1.136", topic: str = "hermes/intent/tv_notification_off"):
    port=1883
    def on_publish(client,userdata,result):             #create function for callback
        print("data published \n")
        pass
    client1= mqtt.Client("control1")                           #create client object
    client1.on_publish = on_publish                          #assign function to callback
    client1.connect(broker,port)                                 #establish connection
    ret= client1.publish(topic,"off") 

def enable_warning(broker: str = "192.168.1.136", topic: str = "hermes/intent/tv_notification_off"):
    port=1883
    def on_publish(client,userdata,result):             #create function for callback
        print("data published \n")
        pass
    client1= mqtt.Client("control1")                           #create client object
    client1.on_publish = on_publish                          #assign function to callback
    client1.connect(broker,port)                                 #establish connection
    ret= client1.publish("hermes/intent/tv_notification_on","on") 