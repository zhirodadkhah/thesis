

import unittest
from sklearn import exceptions
from facilities.file import SimpleFile
from facilities.configure import AddressBank

#vsm
from sklearn.feature_extraction.text import TfidfVectorizer

#norm
from sklearn.metrics.pairwise import cosine_similarity


class VSM:

    class Norm:
        """
        class Norm is a holder
        """
        cosin = "cosin"
        pass


    def __init__(self, stopWords='english'):
        """
        :TODO: I should define Tokenizer and Preproccessing myself.
        """
        self._tfidf_vectorizer = TfidfVectorizer(stop_words=stopWords)
        self._corpus_vector = None
        self._corpus = None
        self._similarity_norm = {self.Norm.cosin:self._consin_similarity}
        pass

    @property
    def corpus(self):
        return self._corpus

    @corpus.setter
    def corpus(self, value):
        self._corpus = value


    def _consin_similarity(self, _X, _Y=None):
        '''

        :param _X:
        :param _Y:
        :return:
        structire: array([[], [], ...]): [][]; innermost list ==> _x[0]=[_y[0], _Y[1], ..., _Y[n]]
        '''
        if _Y is None:
            _Y =  self._corpus_vector
        return cosine_similarity(_X, _Y)

    def vectorize_corpus(self, corpus):
        '''
        The method builds up the model: Matirx[doc,word]. It performs the Fit and Transformation in sequence.
        :param corpus: the collection of documents.
        :return: is the Tf-Idf weighted document-term matrix.
        '''
        self._corpus_vector = self._tfidf_vectorizer.fit_transform(corpus)
        self._corpus = corpus
        return self._corpus_vector

    def vectorize_docs(self, docs):
        '''
        The method transforms the documents into the Tf-Idf weighted vector representation according the fitted
        parameters.
        :param docs: the collection of documents.
        :return: is the set of Tf-Idf weighted vectors.
        '''
        vectorized = None
        try:
            vectorized = self._tfidf_vectorizer.transform(docs)
        except exceptions.NotFittedError:
            raise Exception('No Vocabulary is fitted yet. Prior to vectorizing documents, reference corpus should be vectorizd.')
        return vectorized

    def _merge_retrieved_indices(self, scores, ):

        lst = []
        lst1 = []
        for raw in scores:
            for index, score in enumerate(raw):
                lst.append((score, index))
            lst1.append(lst)
            lst = []
        return lst1


    def _BiSearh(self, lst, l, r, score, mid):

        if r >= l:

            mid = int(l + (r - l) / 2)
            if lst[mid][0] == score:
                return mid

            elif lst[mid][0] > score:
                return self._BiSearh(lst, l, mid - 1, score, mid)

                # Else the element can only be present
            # in right subarray
            else:
                return self._BiSearh(lst, mid + 1, r, score, mid)

        else:
            return mid


    def _filter(self, lst, score):

        index = self._BiSearh(lst, 0, len(lst)-1, score, len(lst)-1)

        while index <len(lst)-1:
            if lst[index+1][0] >= score:
                index+=1
            else:
                break

        return lst[:index+1]



    def _filter_scores(self, scores, min_score_lst):

        """

        :param scores:
        :param min_score_lst:
        :return:
        structure: {score: [[sorted(score, index in corpus) ]]}
        """


        dic = {}
        lst = []

        for score in min_score_lst:
            for raw in scores:
                raw.sort(reverse=-1)
                lst.append(self._filter(raw, score))
            dic.update({score: lst})
            lst = []

        return dic

    def _merge_retrieved_docs(self, queris, relevant_indeices):
        """

        :param queris:
        :param scores:
        :param corpus:
        :return:
        structure: {min_score: [[query, (corpus, score)]]}
        """

        dic = {}
        lst1 = []
        lst = []
        query_i = 0
        for key in relevant_indeices.keys():
            for raw in relevant_indeices[key]:
                for item in raw:
                    lst.append((self.corpus[item[1]], item[0]))
                lst1.append((queris[query_i], lst))
                lst = []
                query_i += 1
            dic.update({key: lst1})
            lst1 = []
            query_i = 0
        return dic




    def retrieve_relevants(self, queris, min_score_list=[0.5], norm=Norm.cosin, merged_doc = False):
        '''
        The method retrieve relevant documents according the each existing element in query. THe query could be a
        single document or contains some. Each document in query is dealt with separatly and its similarity to each
        document in the Corpus id calculated.
        :param queris: is a collection of target documents which are intended to find their matches.
        :param min_score: is the least acceptable score obtained for a pare of document in query and
        document in corpus's weighted matrix.
        :param norm: is the mathematical norm of interest to compare every pare of document in query and
        document in corpus's weighted matrix upon it
        :return: if merged_doc is True: {min_score:[(doc,[(corpus, calculated_score)])]}
        if merged_doc is False:         {min_score:[[(calculated_score, corpus_index)]]}
        '''

        vectors = self.vectorize_docs(queris)
        similarity_scores = self._similarity_norm[norm](vectors)
        merged = self._merge_retrieved_indices(similarity_scores)

        if not isinstance(min_score_list, list):
            min_score_list = list(min_score_list)

        if len(min_score_list)!=0:
              relevants = self._filter_scores(merged, min_score_list)
        else:
            relevants = {'0':merged}

        if merged_doc:
            relevants = self._merge_retrieved_docs(queris,relevants)

        return relevants


def main():
    """
    :todo: save the results to give it to a ploter or a another analyzer.
    :return:
    """
    vsm = VSM()
    corpus = ['The sky is blue.', 'The sun is bright.']
    docs = ['The sun in the sky is bright.', 'We can see the shining sun, the bright sun.']

    vsm.vectorize_corpus(corpus)
    result = vsm.retrieve_relevants(docs, merged_doc= False)
    SimpleFile().save_pickle(result, )

    pass

class VSMTest(unittest.TestCase):

    vsm = VSM()

    def test_corpus_vector_is_None_at_firt(self):

        self.assertIsNone(self.vsm._corpus_vector)

    def test_vectorize_doc_does_not_impact_vector_corpus(self):

        self.vsm.vectorize_corpus(['kjhkjh kjh kj hkjh h k fhgierug.'])
        pre_vector = self.vsm._corpus_vector

        self.vsm.vectorize_docs(['sdfds dfsdf.', 'sdfsdf sdfsd fsdffsdf'])

        self.assertIs(pre_vector, self.vsm._corpus_vector)



if __name__ =="__main__":
    unittest.main()