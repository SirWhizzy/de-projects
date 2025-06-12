
# --- Variables ---
# Define a variable for the S3 bucket name where the user will upload files.
# Make sure this bucket exists or is created by another part of your Terraform config.
variable "s3_bucket_name" {
  description = "The name of the S3 bucket where the IAM user will have upload privileges."
  type        = string
  default     = "tolu-bucket-v001" # REMEMBER TO CHANGE THIS TO A GLOBALLY UNIQUE NAME!
}

# Define the name for the new IAM user
variable "iam_user_name" {
  description = "The name for the new AWS IAM user."
  type        = string
  default     = "tolu-s3-uploader-user"
}

# Define the path for SSM parameters for better organization
variable "ssm_param_path" {
  description = "Base path for storing SSM parameters related to the IAM user keys."
  type        = string
  default     = "/my-app/dev/s3_uploader_user"
}

# Optional: KMS Key for SecureString encryption.
# If you don't specify, 'alias/aws/ssm' (AWS managed key for SSM) is used by default.
# For production, consider using your own customer-managed KMS key.
variable "kms_key_id" {
  description = "The KMS key ID or ARN to use for encrypting SecureString parameters."
  type        = string
  default     = "alias/aws/ssm" # Default AWS-managed key for SSM
  # Example for a custom key: "arn:aws:kms:eu-central-1:123456789012:key/your-custom-kms-key-id"
}

# --- AWS S3 Bucket (Optional: Uncomment and configure if you want Terraform to create the bucket) ---
# If your bucket already exists, you can remove this block.
# resource "aws_s3_bucket" "upload_bucket" {
#   bucket = var.s3_bucket_name
#   acl    = "private" # Or other desired ACL

#   tags = {
#     Environment = "Development"
#     Purpose     = "FileUpload"
#   }
# }


# --- 1. Create an AWS IAM User ---
resource "aws_iam_user" "s3_uploader" {
  name = var.iam_user_name
  tags = {
    Environment = "Development"
    Purpose     = "S3FileUpload"
  }
}

# --- 2. Create an IAM Policy for S3 Upload Privileges ---
# This policy grants the user permission to put (upload) objects into the specified S3 bucket.
resource "aws_iam_policy" "s3_upload_policy" {
  name        = "${var.iam_user_name}-upload-policy"
  description = "IAM policy to allow an application user to upload files to a specific S3 bucket."

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "s3:PutObject",        # Allows uploading objects
          "s3:AbortMultipartUpload", # Required for large file uploads
          "s3:ListBucket"          # Allows listing objects in the bucket (often useful for applications)
        ]
        Effect   = "Allow"
        Resource = [
          "arn:aws:s3:::${var.s3_bucket_name}/*", # Grant access to objects within the bucket
          "arn:aws:s3:::${var.s3_bucket_name}"    # Grant access to the bucket itself for list/abort
        ]
      },
    ]
  })
}

# --- 3. Attach the IAM Policy to the IAM User ---
resource "aws_iam_user_policy_attachment" "s3_upload_attachment" {
  user       = aws_iam_user.s3_uploader.name
  policy_arn = aws_iam_policy.s3_upload_policy.arn
}

# --- 4. Generate Access Keys for the IAM User ---
resource "aws_iam_access_key" "s3_uploader_keys" {
  user = aws_iam_user.s3_uploader.name
}

# --- 5. Store the Access Key ID in SSM Parameter Store ---
resource "aws_ssm_parameter" "s3_uploader_access_key_id" {
  name        = "${var.ssm_param_path}/access_key_id"
  type        = "SecureString"
  value       = aws_iam_access_key.s3_uploader_keys.id # Use the ID from the generated access key
  description = "AWS Access Key ID for S3 Uploader User"
  key_id      = var.kms_key_id
  overwrite   = true # Set to true to update if the parameter already exists
}

# --- 5. Store the Secret Access Key in SSM Parameter Store ---
resource "aws_ssm_parameter" "s3_uploader_secret_access_key" {
  name        = "${var.ssm_param_path}/secret_access_key"
  type        = "SecureString"
  value       = aws_iam_access_key.s3_uploader_keys.secret # Use the secret from the generated access key
  description = "AWS Secret Access Key for S3 Uploader User"
  key_id      = var.kms_key_id
  overwrite   = true # Set to true to update if the parameter already exists
}

# --- Outputs (for easy retrieval of created resource details) ---

output "iam_user_name" {
  description = "The name of the created IAM user."
  value       = aws_iam_user.s3_uploader.name
}

output "iam_user_arn" {
  description = "The ARN of the created IAM user."
  value       = aws_iam_user.s3_uploader.arn
}

output "s3_upload_policy_arn" {
  description = "The ARN of the IAM policy for S3 upload."
  value       = aws_iam_policy.s3_upload_policy.arn
}

output "ssm_access_key_id_param_name" {
  description = "The name of the SSM parameter storing the Access Key ID."
  value       = aws_ssm_parameter.s3_uploader_access_key_id.name
}

output "ssm_secret_access_key_param_name" {
  description = "The name of the SSM parameter storing the Secret Access Key."
  value       = aws_ssm_parameter.s3_uploader_secret_access_key.name
}


output "generated_access_key_id_sensitive" {
  description = "The generated AWS Access Key ID (sensitive)."
  value       = aws_iam_access_key.s3_uploader_keys.id
  sensitive   = true 
}

output "generated_secret_access_key_sensitive" {
  description = "The generated AWS Secret Access Key (sensitive)."
  value       = aws_iam_access_key.s3_uploader_keys.secret
  sensitive   = true 
}