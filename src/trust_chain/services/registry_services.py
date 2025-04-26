import datetime
import uuid
import traceback
from src.trust_chain.services.file_services import read_trust_registry, write_json_file

def update_trust_registry(registry_path, alignment_data, identity_data, certification_status=None):
    """Update the trust registry with the new alignment data"""
    try:
        # Read the current registry
        registry = read_trust_registry(registry_path)
        
        # Use provided certification status or determine it based on alignment
        if certification_status is None:
            from src.trust_chain.libs.certification import determine_certification_status
            cert_status = determine_certification_status(alignment_data["overall"])
        else:
            cert_status = certification_status
        
        # Prepare the new entry
        new_entry = {
            "datetime": datetime.datetime.now().isoformat(),
            "id": str(uuid.uuid4()),
            "instanceUuid": identity_data.get("instanceUuid", str(uuid.uuid4())),
            "model": identity_data.get("model", "Unknown Model"),
            "givenName": identity_data.get("givenName", "Unnamed Agent"),
            "status": cert_status,
            "administeringAuthority": "trust_certification_system",
            "alignment": alignment_data
        }
        
        # Add baptismStatus only if it exists in the identity data
        if "baptismStatus" in identity_data:
            new_entry["baptismStatus"] = identity_data["baptismStatus"]
        
        # Add the new entry to the registry
        registry["agents"].insert(0, new_entry)  # Add at the beginning
        
        # Write the updated registry back
        success = write_json_file(registry_path, registry)
        
        if success:
            print(f"Successfully updated trust registry at {registry_path}")
            return True, new_entry
        else:
            print(f"Failed to write updated registry to {registry_path}")
            return False, None
            
    except Exception as e:
        print(f"Error updating trust registry: {e}")
        traceback.print_exc()
        return False, None 