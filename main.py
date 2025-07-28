import os
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient


# =============================================================================
# STEP 1: CREATE SAMPLE FILES FOR TESTING
# =============================================================================

def create_sample_files():
    """
    Create sample files if they don't exist in the current directory.
    Creates both a .txt file and attempts to create a .docx file.
    """
    # Create sample1.txt if it doesn't exist
    if not os.path.exists('sample1.txt'):
        with open('sample1.txt', 'w') as f:
            f.write("This is a sample text file for Azure Blob Storage testing.")
        print("Created sample1.txt")

    # Create sample2.docx if it doesn't exist (requires python-docx library)
    if not os.path.exists('sample2.docx'):
        try:
            from docx import Document
            doc = Document()
            doc.add_heading('Azure Blob Demo', 0)
            doc.add_paragraph('This is a sample Word document for blob upload testing.')
            doc.save('sample2.docx')
            print("Created sample2.docx\n")
        except ImportError:
            print("Warning: python-docx not installed. Creating sample2.txt instead.")
            with open('sample2.txt', 'w') as f:
                f.write("Sample document content (as .txt since docx library not available)")


# Execute the function to create sample files
create_sample_files()

# =============================================================================
# STEP 2: CONFIGURE AZURE STORAGE CONNECTION
# =============================================================================

# Storage account information
account_url = "https://<your_storage_account_name>.blob.core.windows.net/"

# Authenticate using DefaultAzureCredential (uses Azure CLI login, Managed Identity, etc.)
print("Authenticating with Azure...")
credential = DefaultAzureCredential()
blob_service_client = BlobServiceClient(account_url=account_url, credential=credential)

# =============================================================================
# STEP 3: CREATE BLOB CONTAINER
# =============================================================================

# Define container name and get container client
container_name = 'mytestcontainer'
container_client = blob_service_client.get_container_client(container_name)

# Attempt to create the container (handle case where it already exists)
try:
    container_client.create_container()
    print(f"Container '{container_name}' created successfully!")
except Exception as e:
    print(f"Container may already exist: {e}")

# =============================================================================
# STEP 4: UPLOAD FILES TO BLOB STORAGE
# =============================================================================

# Define list of files to upload
upload_files = ['sample1.txt', 'sample2.docx']

print(f"\nStarting upload of {len(upload_files)} files...")

# Loop through each file and upload to blob storage
for local_file in upload_files:
    try:
        # Check if the file exists locally before attempting upload
        if not os.path.exists(local_file):
            print(f"⚠Warning: File '{local_file}' not found. Skipping.")
            continue

        # Open file in binary mode and upload to blob storage
        with open(local_file, 'rb') as data:
            blob_client = container_client.get_blob_client(local_file)
            blob_client.upload_blob(data, overwrite=True)
            print(f"Uploaded: {local_file}")

    except Exception as e:
        print(f"Error uploading {local_file}: {e}")

# =============================================================================
# STEP 5: LIST ALL BLOBS IN THE CONTAINER
# =============================================================================

print(f"\nListing all blobs in container '{container_name}':")
try:
    blobs = container_client.list_blobs()
    blob_count = 0
    for blob in blobs:
        print(f"   - {blob.name}")
        blob_count += 1

    if blob_count == 0:
        print("   (No blobs found in container)")
    else:
        print(f"   Total blobs: {blob_count}")

except Exception as e:
    print(f"Error listing blobs: {e}")

# =============================================================================
# STEP 6: DOWNLOAD BLOBS FROM STORAGE
# =============================================================================

print(f"\nStarting download process...")
for src_blob_name in upload_files:
    try:
        # Skip if file doesn't exist (wasn't uploaded successfully)
        if not os.path.exists(src_blob_name):
            print(f"Skipping {src_blob_name} - original file not found")
            continue

        # Define output filename with "downloaded_" prefix
        downloaded_filename = "downloaded_" + src_blob_name

        # Get blob client for the specific blob
        blob_client = container_client.get_blob_client(src_blob_name)

        # Download the blob to local file
        with open(downloaded_filename, "wb") as download_file:
            download_stream = blob_client.download_blob()
            download_file.write(download_stream.readall())
            print(f"Downloaded '{src_blob_name}' as '{downloaded_filename}'")

    except Exception as e:
        print(f"Error processing {src_blob_name}: {e}")

# =============================================================================
# STEP 7: DELETE THE CONTAINER (AND ALL BLOBS INSIDE)
# =============================================================================

print(f"\nDeleting container '{container_name}'...")
try:
    container_client.delete_container()
    print(f"Container '{container_name}' deleted successfully!")
except Exception as e:
    print(f"Error deleting container: {e}")

# =============================================================================
# FINAL VERIFICATION
# =============================================================================

print(f"\nLocal files in directory:")
for file in ['sample1.txt', 'sample2.docx', 'downloaded_sample1.txt', 'downloaded_sample2.docx']:
    if os.path.exists(file):
        print(f"   [FOUND] {file}")
    else:
        print(f"   [MISSING] {file}")

# =============================================================================
# SCRIPT COMPLETION
# =============================================================================

print(f"\nScript execution completed!")