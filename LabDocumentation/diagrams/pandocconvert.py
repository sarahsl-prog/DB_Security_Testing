from pathlib import Path
import sys
import subprocess
import shutil

# Try to import pypandoc first (works with pip-installed pandoc)
pypandoc = None
pandoc_cmd = None
use_pypandoc = False

try:
	import pypandoc  # type: ignore
	use_pypandoc = True
	print("Using pypandoc for conversion\n")
except ImportError:
	# Fall back to subprocess with pandoc binary
	pandoc_cmd = shutil.which('pandoc')

	if not pandoc_cmd:
		# Try common Windows installation paths
		possible_paths = [
			r"C:\Program Files\Pandoc\pandoc.exe",
			r"C:\Program Files (x86)\Pandoc\pandoc.exe",
			r"C:\Users\{}\AppData\Local\Pandoc\pandoc.exe".format(Path.home().name),
		]

		for path in possible_paths:
			if Path(path).exists():
				pandoc_cmd = path
				break
		else:
			pandoc_cmd = None

	if not pandoc_cmd:
		print("ERROR: pandoc not found!")
		print("\nYou have two options:")
		print("\nOption 1: Install pypandoc (works with pip):")
		print("  pip install pypandoc")
		print("\nOption 2: Install pandoc binary:")
		print("  Download from: https://pandoc.org/installing.html")
		print("  Or run: winget install JohnMacFarlane.Pandoc")
		print("\nAfter installation, restart your terminal/IDE")
		sys.exit(1)

	print(f"Using pandoc binary: {pandoc_cmd}\n")

# Find all .md files in the current directory
md_files = list(Path('.').glob('*.md'))

if not md_files:
	print("No .md files found in the current directory.")
else:
	print(f"Found {len(md_files)} markdown file(s) to convert:\n")

	success_count = 0
	error_count = 0

	for md in md_files:
		md_path = Path(md)
		output = md_path.with_suffix('.docx')

		try:
			print(f"Converting: {md_path.name} -> {output.name}...")

			if use_pypandoc and pypandoc:
				# Use pypandoc method
				pypandoc.convert_file(
					str(md_path),
					'docx',
					outputfile=str(output)
				)
			elif pandoc_cmd:
				# Use subprocess method
				result = subprocess.run(
					[pandoc_cmd, str(md_path), '-o', str(output)],
					capture_output=True,
					text=True,
					check=True
				)
			else:
				raise RuntimeError("No pandoc method available")

			print(f"  ✓ Success: {output.name}")
			success_count += 1
		except Exception as e:
			print(f"  ✗ Error converting {md_path.name}:")
			print(f"    {str(e)}")
			error_count += 1

	print(f"\n{'='*50}")
	print(f"Conversion complete!")
	print(f"  Successful: {success_count}")
	print(f"  Failed: {error_count}")
