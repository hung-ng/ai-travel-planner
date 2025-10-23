FROM node:18-alpine

WORKDIR /app

# package files
COPY package*.json ./

# install dependencies
RUN npm install

# source code
COPY . .

# port
EXPOSE 3000

# start development server
CMD ["npm", "run", "dev"]
