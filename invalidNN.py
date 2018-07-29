import tensorflow as tf
from random import shuffle


def mul(*args):
    k = 1
    for a in args:
        k *= a
    return k


class layer:  # 얘는 객체 속성 repr? 하면 layer(layer : 'FC', activate_function : 'sigmoid' ~~~) 이렇게 나오게
    def __init__(self, layer: str, activate_function: str, dropout: int = None):
        # 범용 속성
        self.layer = layer
        self.activate = activate_function
        self.dropout = dropout


class FullyConnected(layer):
    def __init__(self, activate_function, units, dropout = 0):
        super().__init__('FC', activate_function, dropout)

        self.weight = self.bias = None
        self.units = units


class Conv(layer):
    def __init__(self, activate_function, padding, stride, filters, filter_shape, dropout = 0):
        super().__init__('Conv', activate_function, dropout)

        self.filter = self.bias = None
        self.filter_shape = filter_shape
        self.channels = filters

        self.padding = padding
        self.stride = stride


class Pooling(layer):
    def __init__(self, pooling, stride, padding, size, activate_function = None, dropout = 0):
        super().__init__('Pooling', activate_function, dropout)

        self.pooling = pooling
        self.stride = stride
        self.padding = padding

        self.size = size
        self.channels = 0


class NeuralNetwork:
    def __init__(self, layers, input_units): # 신경망 검사, 가중치/필터 초기화, 그래프 작성
        activate_function = {
            'sigmoid' : tf.nn.sigmoid,
            'relu' : tf.nn.relu,
            'softmax' : tf.nn.softmax,
            'tanh' : tf.nn.tanh,
            None : lambda x: x
        }
        if isinstance(input_units, int):
            input_units = [input_units]
        self.input_data = tf.placeholder(tf.float32, [None, *input_units])
        batch_size = self.input_data.shape[0]
        flow = self.input_data

        for l, layer in enumerate(layers):
            if isinstance(layer, FullyConnected):
                # 가중치 초기화
                layer.weight = tf.Variable(
                    tf.random_normal([input_units[0] if l == 0 else layers[l-1].units, layer.units])
                )/tf.sqrt(float(input_units[0] if l == 0 else layers[l-1].units))  # Xaiver..?

                layer.bias = tf.Variable(tf.random_normal([1]))

                # 그래프 작성
                if isinstance(layers[l-1], Conv) or isinstance(layers[l-1], Pooling):
                    flow = tf.reshape(flow, [-1, mul(layers[l-1].shape)/batch_size])

                flow = activate_function[layer.activate](tf.matmul(flow, layer.weight) + layer.bias)

            elif isinstance(layer, Conv):
                # 필터 초기화
                layer.filter = tf.Variable(
                    tf.random_normal([*layer.filter_shape, input_units[-1] if l ==0 else layers[l-1].channels, layer.channels])
                )
                layer.bias = tf.Variable(tf.random_normal([layer.channels]))

                # 그래프 작성
                flow = activate_function[layer.activate](
                    tf.nn.conv2d(network, layer.filter, layer.stride, layer.padding) + layer.bias
                )

            elif isinstance(layer, Pooling):
                layer.channels = layers[l-1].channels

                pooling = tf.nn.avg_pool if layer.pooling == 'avg' else tf.nn.max_pool
                flow = activate_function[layer.activate](pooling(flow, layer.size, layer.stride, layer.padding))

        self.output = flow
        self.saver = tf.train.Saver()

    def train(self, training_dataset, batch_size, loss_function, optimizer, learning_rate, epoch = 1):
        object_output = tf.placeholder(tf.float32, [None, len(training_dataset[0][1])])

        if loss_function == 'least-square':
            loss = tf.reduce_mean(tf.square(object_output - self.output))
        elif loss_function == 'cross-entopy':
            loss = -tf.reduce_sum(object_output*tf.log(self.output))

        if optimizer == 'gradient_descent':
            train_step = tf.train.GradientDescentOptimizer(learning_rate).minimize(loss)
        elif optimizer == 'adam':
            train_step = tf.train.AdamOptimizer(learning_rate).minimize(loss)

        init = tf.global_variables_initializer()

        with tf.Session() as sess:
            sess.run(init)

            for _ in range(epoch):
                shuffle(training_dataset)
                dataset_length = len(training_dataset)

                for b in range(round(dataset_length/batch_size)):
                    batch = training_dataset[b*batch_size : (b+1)*batch_size]

                    x_batch = [b[0] for b in batch]
                    y_batch = [b[1] for b in batch]

                    sess.run(train_step,
                             feed_dict={self.input_data: x_batch, object_output: y_batch})

            for layer in layers:
                if not isinstance(layer, Pooling):
                    if isinstance(layer, FullyConnected):
                        layer.weight = sess.run(layer.weight)
                    elif isinstance(layer, Conv):
                        layer.filter = sess.run(layer.filter)
                    layer.bias = sess.run(bias)

    def query(self, input_data):
        pass # 신경망 질의

    def __getitem__(self, item):
        pass


if __name__ == '__main__':
    main()

def main():
    sample_network = [
        FullyConnected('Sigmoid', 200),
        FullyConnected('Softmax', 10)
    ]

    testAI = NeuralNetwork(sample_network, 784)