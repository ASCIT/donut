> "So we ask ourselves, what are donuts? There are three types of people in this world. Those who eat the donut and leave. Those who look at the donut and wish they could eat it and leave. And those who make the donut. We make the donut. We are Donut Devteam. And so now when you are hungry, Donut Devteam will make you donuts." - Rahul Bachal

The Amazon AWS EC2 instance for donut is used for the site rewrite. The account is registered with the donut email donutascit@gmail.com. Go to the AWS console and reboot the EC2 instance if Donut is down.

# Notable config settings
* It is set up in the US West (Oregon) region - also recommended by IMSS because it's new and gets regular updates as opposed to the NorCal one.
* The full config notes https://docs.google.com/document/d/1F_GCZ9r16P6zUqCr9TGYySC8OroARAyeCSLmHnoEyjQ/edit
* It is set up so that you can only SSH into the AWS server from Caltech. If you need to do it from outside of Caltech, you will need to use the Caltech VPN client and select "3: Tunnel All" in the connection startup settings.
* It is set up with a static IP.
* Domain: ec2-35-162-204-135.us-west-2.compute.amazonaws.com

# Routine Task
* Obtain the donut email and AWS account credentials from the previous Devteam lead.
* On Donut Email, transfer 2-Factor Authentication to new lead.
* On AWS account, add a new credit card for payment and delete the old one. ASCIT will reimburse the charges.