import { v4 as uuidv4 } from 'uuid';
import { writeFileSync } from 'fs';
import path from 'path';

const uploadFile = async (file: File) => {
	const filename = uuidv4() + path.extname(file.name);

	writeFileSync(
		path.join(process.cwd(), 'static', 'uploads', filename),
		Buffer.from(await file.arrayBuffer())
	);

	return '/uploads/' + filename;
};

const uploadService = {
	uploadFile
};

export default uploadService;
