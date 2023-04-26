import { ConfluenceSettings } from "src/Settings";
import { BinaryFile, FilesToUpload, LoaderAdaptor, MarkdownFile } from ".";
import { lookup } from "mime-types";
import * as fs from "fs/promises";
import * as path from "path";
import matter, { stringify } from "gray-matter";
import {
	ConfluencePerPageAllValues,
	ConfluencePerPageConfig,
	conniePerPageConfig,
} from "../ConniePageConfig";

export class FileSystemAdaptor implements LoaderAdaptor {
	settings: ConfluenceSettings;
	folderPath: string;

	constructor(settings: ConfluenceSettings, folderPath: string) {
		this.settings = settings;
		this.folderPath = folderPath;
	}

	async getFileContent(absoluteFilePath: string) {
		const fileContent = await fs.readFile(absoluteFilePath, "utf-8");
		const { data, content } = matter(fileContent);
		return { data, content };
	}

	async updateMarkdownValues(
		absoluteFilePath: string,
		values: Partial<ConfluencePerPageAllValues>
	): Promise<void> {
		if (!(await fs.stat(absoluteFilePath)).isFile()) {
			return;
		}

		const fileContent = await this.getFileContent(absoluteFilePath);

		const config = conniePerPageConfig;

		const fm: { [key: string]: unknown } = {};
		for (const propertyKey in config) {
			if (!config.hasOwnProperty(propertyKey)) {
				continue;
			}

			const { key } =
				config[propertyKey as keyof ConfluencePerPageConfig];
			const value =
				values[propertyKey as keyof ConfluencePerPageAllValues];
			if (propertyKey in values) {
				fm[key] = value;
			}
		}

		const updatedData = stringify(fileContent, fm);
		await fs.writeFile(absoluteFilePath, updatedData);
	}

	async loadMarkdownFile(absoluteFilePath: string): Promise<MarkdownFile> {
		const { data, content: contents } = await this.getFileContent(
			absoluteFilePath
		);

		const folderName = path.basename(path.parse(absoluteFilePath).dir);
		const fileName = path.basename(absoluteFilePath);

		const extension = path.extname(fileName);
		const pageTitle = path.basename(fileName, extension);

		return {
			folderName,
			absoluteFilePath,
			fileName,
			pageTitle,
			contents,
			frontmatter: data,
		};
	}

	async loadMarkdownFiles(folderPath: string): Promise<MarkdownFile[]> {
		const files: MarkdownFile[] = [];

		const entries = await fs.readdir(folderPath, {
			withFileTypes: true,
		});

		for (const entry of entries) {
			const absoluteFilePath = path.join(folderPath, entry.name);

			if (entry.isFile() && path.extname(entry.name) === ".md") {
				const file = await this.loadMarkdownFile(absoluteFilePath);
				files.push(file);
			} else if (entry.isDirectory()) {
				const subFiles = await this.loadMarkdownFiles(absoluteFilePath);
				files.push(...subFiles);
			}
		}

		return files;
	}

	async getMarkdownFilesToUpload(): Promise<FilesToUpload> {
		const files = await this.loadMarkdownFiles(this.folderPath);
		const filesToPublish = [];
		for (const file of files) {
			try {
				const frontMatter = file.frontmatter;

				if (
					(file.absoluteFilePath.startsWith(
						this.settings.folderToPublish
					) &&
						(!frontMatter ||
							frontMatter["connie-publish"] !== false)) ||
					(frontMatter && frontMatter["connie-publish"] === true)
				) {
					filesToPublish.push(file);
				}
			} catch {
				//ignore
			}
		}

		return filesToPublish;
	}

	async readBinary(
		searchPath: string,
		referencedFromFilePath: string
	): Promise<BinaryFile | false> {
		const absoluteFilePath = await this.findClosestFile(
			searchPath,
			path.dirname(referencedFromFilePath)
		);

		if (absoluteFilePath) {
			const fileContents = await fs.readFile(absoluteFilePath);

			const mimeType =
				lookup(path.extname(absoluteFilePath)) ||
				"application/octet-stream";
			return {
				contents: fileContents,
				filePath: absoluteFilePath.replace(this.folderPath, ""),
				filename: path.basename(absoluteFilePath),
				mimeType: mimeType,
			};
		}

		return false;
	}

	private async findClosestFile(
		fileName: string,
		startingDirectory: string
	): Promise<string | null> {
		const matchingFiles: string[] = [];
		const directoriesToSearch: string[] = [startingDirectory];

		while (directoriesToSearch.length > 0) {
			const currentDirectory = directoriesToSearch.shift();
			if (!currentDirectory) {
				continue;
			}

			const entries = await fs.readdir(currentDirectory, {
				withFileTypes: true,
			});

			for (const entry of entries) {
				const fullPath = path.join(currentDirectory, entry.name);

				if (
					entry.isFile() &&
					entry.name.toLowerCase() === fileName.toLowerCase()
				) {
					matchingFiles.push(fullPath);
				} else if (
					entry.isDirectory() &&
					fullPath.startsWith(this.folderPath)
				) {
					directoriesToSearch.push(fullPath);
				}
			}
		}

		if (matchingFiles.length > 0) {
			return matchingFiles[0];
		}

		const parentDirectory = path.dirname(startingDirectory);

		if (parentDirectory === startingDirectory) {
			return null;
		}

		return await this.findClosestFile(fileName, parentDirectory);
	}
}
