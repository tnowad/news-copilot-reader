export const getErrorFieldMessage = (
	error: { field: string; message: string }[],
	field: string
) => {
	return error.find((e) => e.field === field)?.message;
};
