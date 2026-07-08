resource_group_name = "StudentDropoutRG-TF"

location = "southeastasia"

vnet_name = "student-vnet"

subnet_name = "student-subnet"

public_ip_name = "student-public-ip"

nsg_name = "student-nsg"

nic_name = "student-nic"

vm_name = "student-vm"

vm_size = "Standard_B2s"

admin_username = "azureuser"

admin_password = "Student@2026DevOps"

address_space = [
  "10.0.0.0/16"
]

subnet_prefix = [
  "10.0.1.0/24"
]