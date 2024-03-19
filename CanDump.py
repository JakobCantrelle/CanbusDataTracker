import subprocess
import curses
import time
import random

CanIdCounts = {}

CanAmount = 3500

class CarStatus:
    def __init__(self):
        self.brakePressure = 0
        self.gear = 'P'
        self.parkingBrake = 'engaged'
        self.headlights = 'Off'
        self.Odometer = 0
        self.doorsOpen = "00000000"
        self.doorString = ""
        self.status = ""
    
    def UpdateStatus(self,
                        brakePressure=None,
                        gear=None,
                        parkingBrake=None,
                        headlights=None,
                        doorsOpen=None,
                        status=None,
                        Odometer=None):
        


        if brakePressure is not None:
            self.brakePressure = brakePressure
        if gear is not None:
            self.gear = gear
        if parkingBrake is not None:
            self.parkingBrake = parkingBrake
        if headlights is not None:
            self.headlights = headlights
        if Odometer is not None:
            self.Odometer = Odometer
        if doorsOpen is not None:
            self.doorString = ""
            self.doorsOpen = doorsOpen
            if self.doorsOpen[0] == "1":
                self.doorString = self.doorString + "Trunk, "
            if self.doorsOpen[1] == "1":
                self.doorString = self.doorString + "Passenger back door, "
            if self.doorsOpen[2] == "1":
                self.doorString = self.doorString + "Driver back door, "
            if self.doorsOpen[3] == "1":
                self.doorString = self.doorString + "Passenger's door, "
            if self.doorsOpen[4] == "1":
                self.doorString = self.doorString + "Driver's door, "
            if len(self.doorString) > 1:
                self.doorString = self.doorString.removesuffix(", ")
            
        if status is not None:
            self.status = status
        self.DisplayStatus()
    
    def DisplayStatus(self):

        print("\033[F\033[K\033[F\033[K\033[F\033[K\033[F\033[K\033[F\033[K\033[F\033[K\033[F\033[K\033[F\033[K", end='')
        print(f"Brake pressure: {self.brakePressure} ({(self.brakePressure / 255) * 100}%)")
        print(f"Gear: {self.gear}")
        print(f"Parking brake: {self.parkingBrake}")
        print(f"Headlights: {self.headlights}")
        print(f"Odometer: {self.Odometer}")
        print(f"Open doors: {self.doorString}")
        print(f"Engine status: {self.status}")

# Example usage:
carStatus = CarStatus()  # Initialize the status
carStatus.DisplayStatus()  # Initial display

def HexToBin(AHex):
    return bin(int(AHex, 16))[2:].zfill(8)

    
    

def ProcessCanMessage(can_message):
    parts = can_message.split()
    CanCode = parts[1]
    if len(parts) > 1:
        can_id = parts[1]
        if can_id in CanIdCounts:
            CanIdCounts[can_id] += 1
        else:
            CanIdCounts[can_id] = 1
        if CanCode == "1CB":
            BrakePressure = int(parts[5], 16)
            carStatus.UpdateStatus(brakePressure=BrakePressure)
        elif CanCode == "58A":
            carStatus.UpdateStatus(parkingBrake="On" if parts[3] == "16" else "Off")
        elif CanCode == "5C5":
            OdometerNum = int(parts[4] + parts[5] + parts[6], 16)
            carStatus.UpdateStatus(Odometer=OdometerNum)
        elif CanCode == "625":
            Lights = parts[4]
            if Lights == "00":
                carStatus.UpdateStatus(headlights="Off")
            elif Lights == "40":
                carStatus.UpdateStatus(headlights="Parking Lights")
            elif Lights == "60":
                carStatus.UpdateStatus(headlights="Normal Lights")
        elif CanCode == "174":
            GearStatus = parts[6]
            if GearStatus == "AA":
                carStatus.UpdateStatus(gear="Park/Neutral")
            elif GearStatus == "99":
                carStatus.UpdateStatus(gear="Reverse")
            elif GearStatus == "BB":
                carStatus.UpdateStatus(gear="Drive")
        elif CanCode == "60D":
            doorbyte = parts[3]
            doorbits = HexToBin(doorbyte)
            carStatus.UpdateStatus(doorsOpen=doorbits)

            enginebyte = parts[4]
            enginebits = HexToBin(enginebyte)
            engineStatus = enginebits[5] + enginebits[6]
            print(engineStatus)
            if engineStatus == "00":
                carStatus.UpdateStatus(status="Off")
            elif engineStatus == "01":
                carStatus.UpdateStatus(status="Infotainment")
            elif engineStatus == "11":
                carStatus.UpdateStatus(status="On")
            elif engineStatus == "10":
                carStatus.UpdateStatus(status="Starting...")

            



def CaptureCanDumpLive():
    try:
        process = subprocess.Popen(['candump', 'can0'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        while True:
            line = process.stdout.readline()
            if not line:
                break  # Exit the loop if no more output is received
            can_id = line.decode().strip()
            ProcessCanMessage(can_id)
    except subprocess.CalledProcessError as e:
        print("Error executing candump:", e)

def PrintCanIdCountsSorted():
    # Sort the dictionary by count in descending order
    sorted_can_id_counts = sorted(CanIdCounts.items(), key=lambda item: item[1], reverse=True)
    
    for can_id, count in sorted_can_id_counts:
        print(f"CAN ID: {can_id}, Count: {count}")

# Example usage
CaptureCanDumpLive()
print("Done")
PrintCanIdCountsSorted()
