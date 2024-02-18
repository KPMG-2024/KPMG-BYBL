import "cheerio";
import { CheerioWebBaseLoader } from "langchain/document_loaders/web/cheerio";
import { RecursiveCharacterTextSplitter } from "langchain/text_splitter";
import { MemoryVectorStore } from "langchain/vectorstores/memory"
import { OpenAIEmbeddings, ChatOpenAI } from "@langchain/openai";
import { pull } from "langchain/hub";
import { ChatPromptTemplate } from "@langchain/core/prompts";
import { StringOutputParser } from "@langchain/core/output_parsers";

import { createStuffDocumentsChain } from "langchain/chains/combine_documents";

const memory = new BufferMemory({
    returnMessages: true,
    memoryKey: 'history',
  });

// DB로 쓰일거
const loader = new CheerioWebBaseLoader(
  "https://lilianweng.github.io/posts/2023-06-23-agent/"
);

const docs = await loader.load();

const textSplitter = new RecursiveCharacterTextSplitter({ chunkSize: 1000, chunkOverlap: 200 });

// 위의 문서를 스플릿해줌.
const splits = await textSplitter.splitDocuments(docs);

const vectorStore = await MemoryVectorStore.fromDocuments(splits, new OpenAIEmbeddings());

// Retrieve and generate using the relevant snippets of the blog.
const retriever = vectorStore.asRetriever();

const prompt = await pull<ChatPromptTemplate>("rlm/rag-prompt");

const model = new ChatOpenAI({
    openAIApiKey: key,
    model: gptVersion,
    temperature: 0.3,
  });

const ragChain = await createStuffDocumentsChain({
  model,
  prompt,
  outputParser: new StringOutputParser(),
})


export const QA = async (prompt) => {
    
    const retrievedDocs = await retriever.getRelevantDocuments(prompt)
  
    // Use chain with retrieved documents as context
    const response = await ragChain.invoke({
        question: "What is task decomposition?",
        context: retrievedDocs,
      })

    return response;
  };