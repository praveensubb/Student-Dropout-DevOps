variable "resource_group_name" {
  default = "StudentDropoutRG-TF"
}

variable "location" {
  default = "southeastasia"
}

variable "vnet_name" {
  default = "student-vnet"
}

variable "subnet_name" {
  default = "student-subnet"
}

variable "public_ip_name" {
  default = "student-public-ip"
}

variable "nsg_name" {
  default = "student-nsg"
}

variable "nic_name" {
  default = "student-nic"
}

variable "vm_name" {
  default = "student-vm"
}

variable "vm_size" {
  default = "Standard_B2s"
}

variable "admin_username" {
  default = "azureuser"
}

variable "admin_password" {
  sensitive = true
}

variable "address_space" {
  default = [
    "10.0.0.0/16"
  ]
}

variable "subnet_prefix" {
  default = [
    "10.0.1.0/24"
  ]
}