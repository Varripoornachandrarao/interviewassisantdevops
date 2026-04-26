output "instance_public_ip" {
  description = "Public IP of the DevOps Server"
  value       = aws_instance.devops_server.public_ip
}

output "vpc_id" {
  description = "ID of the created VPC"
  value       = aws_vpc.main.id
}
