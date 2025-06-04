import os
import tarfile


def compress_folder_to_tar_gz(source_dir, output_filename=None):
    """
    Compress a folder into a .tar.gz archive file.

    Args:
        source_dir (str): Path to the folder to be compressed
        output_filename (str, optional): Name of the output tar.gz file.
                                        If None, uses the folder name + .tar.gz

    Returns:
        str: Path to the created tar.gz file

    Raises:
        FileNotFoundError: If source_dir doesn't exist
    """
    # Check if source directory exists
    if not os.path.exists(source_dir):
        raise FileNotFoundError(f"Source directory '{source_dir}' not found")

    # Create output filename if not provided
    if output_filename is None:
        output_filename = os.path.basename(os.path.normpath(source_dir)) + ".tar.gz"
    elif not output_filename.endswith('.tar.gz'):
        output_filename += '.tar.gz'

    # Get absolute paths
    source_dir = os.path.abspath(source_dir)
    parent_dir = os.path.dirname(source_dir)
    base_dir = os.path.basename(source_dir)

    # Create the tar.gz file
    with tarfile.open(parent_dir + "/" + output_filename, "w:gz") as tar:
        # Change to parent directory to avoid full paths in the archive
        current_dir = os.getcwd()
        os.chdir(parent_dir)

        try:
            # Add the directory to the archive
            tar.add(base_dir)
        finally:
            # Change back to the original directory
            os.chdir(current_dir)

    return parent_dir + "/" + output_filename
