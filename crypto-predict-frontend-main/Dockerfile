FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
EXPOSE 3000
# العلم --host ضروري جداً لكي يعمل localhost:3000 في متصفحك
CMD ["npm", "run", "dev", "--", "--host"]