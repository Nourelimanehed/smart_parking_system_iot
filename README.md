# smart_parking_system_iot
Developing an intelligent parking system designed to automatically guide users to available parking spaces at the lowest cost through a dedicated mobile application.

## User-Centred Parking Process
• User accesses the mobile app and enters the booking details.
• Chooses a payment method and completes the transaction.
• Receives payment confirmation and reservation details.
• As the user approaches the parking facility gate, scans their RFID card.
• Raspberry Pi-controlled RFID ID reader verifies the card details and checks with
the database for reservation validity.
• Distance sensor measures the proximity of the user’s car to the gate.
• Gate opens automatically when the user is close enough. The app starts a countdown
timer.
• Gate closes automatically after the vehicle enters, ensuring only authorized users
get in.
• Users have the option to extend their booking time.

