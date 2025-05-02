#!/usr/bin/env bash
#
# Update component registration to use the tekton-register utility
#
# This script updates launch scripts for all components to use the unified
# tekton-register utility instead of individual register_with_hermes.py scripts.
#

# Source utility scripts
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LIB_DIR="${SCRIPT_DIR}/../lib"

source "${LIB_DIR}/tekton-utils.sh"
source "${LIB_DIR}/tekton-ports.sh"
source "${LIB_DIR}/tekton-process.sh"
source "${LIB_DIR}/tekton-config.sh"

# Find Tekton root directory
tekton_find_root

# Paths
TEKTON_DIR="$TEKTON_ROOT"
CONFIG_DIR="${TEKTON_DIR}/config/components"
REGISTER_SCRIPT="${TEKTON_DIR}/scripts/tekton-register"

# Check if the tekton-register script exists
if [[ ! -f "${REGISTER_SCRIPT}" ]]; then
    tekton_error "tekton-register script not found: ${REGISTER_SCRIPT}"
    exit 1
fi

# Function to update a component's launch script
update_component_launch_script() {
    local component="$1"
    local component_dir="${TEKTON_DIR}/${component}"
    local launch_script="${component_dir}/setup.sh"
    local register_script="${component_dir}/register_with_hermes.py"
    local config_file="${CONFIG_DIR}/$(echo "${component}" | tr '[:upper:]' '[:lower:]').yaml"
    
    # Check if this component's config file exists
    if [[ ! -f "${config_file}" ]]; then
        tekton_warning "Config file not found for ${component}: ${config_file}"
        return 1
    fi
    
    # Check if the component has a launch script
    if [[ ! -f "${launch_script}" ]]; then
        tekton_warning "Launch script not found for ${component}: ${launch_script}"
        return 1
    fi
    
    # Check if the component has a registration script
    if [[ ! -f "${register_script}" ]]; then
        tekton_warning "Registration script not found for ${component}: ${register_script}"
        return 1
    }
    
    # Back up the launch script
    cp "${launch_script}" "${launch_script}.bak"
    tekton_info "Backed up ${launch_script} to ${launch_script}.bak"
    
    # Update the launch script
    if grep -q "register_with_hermes.py" "${launch_script}"; then
        # Get the component ID from the config file
        local component_id=$(grep -A1 "id:" "${config_file}" | tail -n1 | sed 's/.*"\(.*\)".*/\1/')
        
        # Replace the registration command with tekton-register
        sed -i.tmp "s|python.*register_with_hermes.py.*|${REGISTER_SCRIPT} register --component ${component_id} --config ${config_file}|g" "${launch_script}"
        rm -f "${launch_script}.tmp"
        
        tekton_success "Updated ${launch_script} to use tekton-register"
        return 0
    else
        tekton_warning "No registration command found in ${launch_script}"
        return 1
    fi
}

# Function to create symlinks to shared utils
create_shared_utils_symlinks() {
    local utils_dir="${HOME}/utils"
    mkdir -p "${utils_dir}"
    
    # Create symlinks to scripts/bin directory
    for script in "${TEKTON_DIR}/scripts/bin"/*; do
        if [[ -f "${script}" && -x "${script}" ]]; then
            local script_name=$(basename "${script}")
            local symlink="${utils_dir}/${script_name}"
            
            # Create symlink if it doesn't exist
            if [[ ! -L "${symlink}" ]]; then
                ln -s "${script}" "${symlink}"
                tekton_info "Created symlink: ${symlink} -> ${script}"
            fi
        fi
    done
    
    # Create symlinks to utility scripts
    for script in "${LIB_DIR}"/*.sh; do
        if [[ -f "${script}" ]]; then
            local script_name=$(basename "${script}")
            local symlink="${utils_dir}/${script_name}"
            
            # Create symlink if it doesn't exist
            if [[ ! -L "${symlink}" ]]; then
                ln -s "${script}" "${symlink}"
                tekton_info "Created symlink: ${symlink} -> ${script}"
            fi
        fi
    done
}

# Main function
main() {
    tekton_header "Updating Component Registration Scripts"
    
    # Update component launch scripts
    for component_dir in "${TEKTON_DIR}"/*; do
        # Only process directories that might be components
        if [[ -d "${component_dir}" && ! "${component_dir}" == *node_modules* && ! "${component_dir}" == *.git* ]]; then
            component=$(basename "${component_dir}")
            
            # Skip non-component directories
            if [[ "${component}" == "scripts" || "${component}" == "config" || "${component}" == "docs" ]]; then
                continue
            fi
            
            tekton_info "Processing component: ${component}"
            update_component_launch_script "${component}"
        fi
    done
    
    # Create symlinks to shared utilities
    tekton_info "Creating symlinks to shared utilities in ~/utils"
    create_shared_utils_symlinks
    
    tekton_success "Component registration update complete"
}

# Execute main function
main