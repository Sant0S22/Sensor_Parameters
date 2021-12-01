import telnetlib
import getpass #Libreria per acquisizione password?

HOST = "192.168.1.1"
user = str(input("Inserisci il tuo account remoto: "))
password = getpass.getpass()

tn = telnetlib.Telnet(HOST)

tn.read_until("login: ")
tn.write(user + "\n")
if password:
    tn.read_until("Password: ")
    tn.write(password + "\n")

while rospy.is_shutdown() 

    tn.write("status\n")
    tn.read_until("Location: ")
    coordinates = tn.read_until("LocalizationScore :");
    rospy.sleep()

